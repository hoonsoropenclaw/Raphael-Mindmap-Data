#!/usr/bin/env python3
"""
meeting_pipeline.py — 會議錄音到行事曆待辦 pipeline (Day 1 scaffolding)

Stage 1: pydub 切 mp3 → <25MB 段
Stage 2: OpenAI Whisper API (whisper-1) 逐段轉錄
Stage 3: Gemini (response_schema JSON) 萃取決議
Stage 4: Google Calendar events.insert 帶 extendedProperties.source
Trace:   SQLite trace 表，audio_hash UNIQUE → idempotent
Run:     python meeting_pipeline.py <audio.mp3> [--dry-run]

Day 1 範圍：Stage 1 + Stage 2 的 CLI scaffolding + trace 表 + idempotency check
Day 2 範圍：Stage 3 + Stage 4 + Gemini / Google API 串接
Day 3 範圍：錯誤處理強化 + RUNLOG 撰寫 + Playwright 視覺驗證

教訓對齊（參考 sops/code/SOP.md）：
- 金鑰一律從環境變數讀
- 破壞性動作不提供 --force / --no-backup；改走 --dry-run
- 外部 I/O 都要有可行動錯誤訊息
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path

CHUNK_SIZE_MB = 24  # Whisper 上限 25MB，留 1MB buffer
DEFAULT_DB = Path.home() / ".config" / "meeting-pipeline" / "trace.db"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def init_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS traces (
            audio_hash TEXT PRIMARY KEY,
            audio_path TEXT NOT NULL,
            sha256_at_run TEXT NOT NULL,
            status TEXT NOT NULL,         -- pending/staged/transcribed/parsed/calendared/failed
            stage TEXT,                   -- 失敗時的最後 stage
            transcript_path TEXT,
            decisions_json TEXT,
            calendar_event_ids TEXT,      -- JSON array of event IDs
            error TEXT,
            cost_usd REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def stage1_chunk(audio_path: Path, out_dir: Path) -> list[Path]:
    """pydub 切 < 25MB 段（粗略以 1MB ≈ 1 分鐘 mp3 估算切點）。"""
    from pydub import AudioSegment
    out_dir.mkdir(parents=True, exist_ok=True)
    audio = AudioSegment.from_file(audio_path)
    # 粗略：24MB / (audio 總 MB) × 總時長 ms = 每段時長 ms
    total_bytes = audio_path.stat().st_size
    total_ms = len(audio)
    if total_bytes <= CHUNK_SIZE_MB * 1024 * 1024:
        # 不用切，直接複製（用原始檔就好）
        return [audio_path]
    bytes_per_ms = total_bytes / total_ms
    chunk_ms = int(CHUNK_SIZE_MB * 1024 * 1024 / bytes_per_ms * 0.95)  # 5% buffer
    chunks: list[Path] = []
    for i in range(0, total_ms, chunk_ms):
        seg = audio[i : i + chunk_ms]
        chunk_path = out_dir / f"{audio_path.stem}-{i // 1000:06d}s.mp3"
        seg.export(chunk_path, format="mp3", bitrate="64k")  # 壓低 bitrate 確保 < 25MB
        chunks.append(chunk_path)
    return chunks


def stage2_transcribe(chunk_paths: list[Path], dry_run: bool) -> str:
    """Whisper API 串接；dry_run 時回傳 mock transcript."""
    if dry_run:
        return json.dumps({
            "text": "[DRY-RUN MOCK] 主席：今天討論季報。決議：總監：下週三前完成。",
            "language": "zh",
            "segments": [
                {"start": 0, "end": 5, "text": "主席：今天討論季報"},
                {"start": 5, "end": 12, "text": "決議：總監下週三前完成"},
            ],
        }, ensure_ascii=False, indent=2)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("缺少 OPENAI_API_KEY；用 --dry-run 跳過")
    try:
        from openai import OpenAI
    except ImportError:
        raise SystemExit("請先 pip install openai")
    client = OpenAI(api_key=api_key)
    parts: list[str] = []
    for p in chunk_paths:
        with p.open("rb") as f:
            r = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="zh",
                prompt="以下是會議錄音，常用詞：季報、總監、處務、請假、加班。",
            )
        parts.append(r.text)
    return "\n".join(parts)


def cmd_run(args: argparse.Namespace) -> int:
    audio = Path(args.audio).resolve()
    if not audio.exists():
        raise SystemExit(f"找不到音檔：{audio}")
    audio_hash = sha256_file(audio)
    db_path = Path(args.db).expanduser()
    conn = init_db(db_path)
    row = conn.execute(
        "SELECT status, audio_path, sha256_at_run FROM traces WHERE audio_hash = ?",
        (audio_hash,),
    ).fetchone()
    if row:
        prev_status, prev_path, prev_sha = row
        if prev_sha == audio_hash and prev_status == "calendared":
            print(f"跳過：已處理過 {audio_hash}（status={prev_status}）")
            conn.close()
            return 0
        print(f"警告：找到歷史記錄 status={prev_status}，繼續處理（idempotency）")
    work_dir = Path(args.work_dir).expanduser() / audio_hash[:12]
    work_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = work_dir / "transcript.txt"
    try:
        chunk_dir = work_dir / "chunks"
        chunks = stage1_chunk(audio, chunk_dir)
        print(f"[stage1] 切成 {len(chunks)} 段（{CHUNK_SIZE_MB}MB/段）")
        conn.execute(
            "INSERT OR REPLACE INTO traces (audio_hash, audio_path, sha256_at_run, status, transcript_path, updated_at) "
            "VALUES (?, ?, ?, 'staged', ?, CURRENT_TIMESTAMP)",
            (audio_hash, str(audio), audio_hash, str(transcript_path)),
        )
        conn.commit()
        print(f"[stage2] 轉錄中…（dry_run={args.dry_run}）")
        transcript = stage2_transcribe(chunks, dry_run=args.dry_run)
        transcript_path.write_text(transcript, encoding="utf-8")
        conn.execute(
            "UPDATE traces SET status=?, updated_at=CURRENT_TIMESTAMP WHERE audio_hash=?",
            ("transcribed", audio_hash),
        )
        conn.commit()
        print(f"[完成] transcript: {transcript_path}")
        print(f"[Day 1 範圍] Stage 3 / 4 待 Day 2 實作")
        return 0
    except Exception as e:
        conn.execute(
            "UPDATE traces SET status='failed', stage=?, error=?, updated_at=CURRENT_TIMESTAMP WHERE audio_hash=?",
            ("stage1+stage2", str(e), audio_hash),
        )
        conn.commit()
        raise
    finally:
        conn.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="會議錄音到行事曆待辦 pipeline")
    ap.add_argument("audio", help="輸入 mp3 / wav / m4a 檔")
    ap.add_argument("--db", default=str(DEFAULT_DB), help="trace DB 路徑")
    ap.add_argument("--work-dir", default="~/.local/share/meeting-pipeline", help="工作目錄")
    ap.add_argument("--dry-run", action="store_true", help="跳過實際 API call，回 mock 結果")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run", help="執行 pipeline").set_defaults(func=cmd_run)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())