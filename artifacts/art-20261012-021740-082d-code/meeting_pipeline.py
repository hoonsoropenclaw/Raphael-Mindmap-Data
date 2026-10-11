#!/usr/bin/env python3
"""
meeting_pipeline.py — 會議錄音到行事曆待辦 pipeline

Stage 1: pydub 切 mp3 → <25MB 段
Stage 2: OpenAI Whisper API (whisper-1) 逐段轉錄
Stage 3: Gemini (response_schema JSON) 萃取決議
Stage 4: Google Calendar events.insert 帶 extendedProperties.source
Trace:   SQLite trace 表，audio_hash UNIQUE → idempotent
Run:     python meeting_pipeline.py <audio.mp3> [--dry-run] run

Day 1: Stage 1 + Stage 2 + trace 表 + idempotency check
Day 2: Stage 3 + Stage 4 + Gemini / Google API 串接
Day 3: 錯誤處理強化 + RUNLOG 撰寫 + 視覺驗證

教訓對齊（參考 sops/code/SOP.md）：
- 金鑰一律從環境變數讀
- 破壞性動作不提供 --force / --no-backup；改走 --dry-run
- 外部 I/O 都要有可行動錯誤訊息
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
import sqlite3
import sys
from datetime import date
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
            status TEXT NOT NULL,
            stage TEXT,
            transcript_path TEXT,
            decisions_json TEXT,
            calendar_event_ids TEXT,
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
    total_bytes = audio_path.stat().st_size
    total_ms = len(audio)
    if total_bytes <= CHUNK_SIZE_MB * 1024 * 1024:
        return [audio_path]
    bytes_per_ms = total_bytes / total_ms
    chunk_ms = int(CHUNK_SIZE_MB * 1024 * 1024 / bytes_per_ms * 0.95)
    chunks: list[Path] = []
    for i in range(0, total_ms, chunk_ms):
        seg = audio[i : i + chunk_ms]
        chunk_path = out_dir / f"{audio_path.stem}-{i // 1000:06d}s.mp3"
        seg.export(chunk_path, format="mp3", bitrate="64k")
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


def stage3_extract_decisions(transcript: str, dry_run: bool) -> list[dict]:
    """Stage 3 — Gemini 萃取決議/待辦。
    回傳 decisions 陣列，每筆含 {title, datetime, attendees[], notes}。
    """
    if dry_run:
        return [
            {
                "title": "下週三前完成 Q3 季報彙整",
                "datetime": "2026-10-14T17:00:00+08:00",
                "duration_minutes": 60,
                "attendees": ["director@example.com"],
                "notes": "主席指派，總監接手",
            },
            {
                "title": "回覆總務處加班費請示",
                "datetime": "2026-10-15T12:00:00+08:00",
                "duration_minutes": 30,
                "attendees": ["hr@example.com"],
                "notes": "依人事條例核處",
            },
        ]
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise SystemExit("缺少 GEMINI_API_KEY；用 --dry-run 跳過")
    try:
        import google.generativeai as genai
    except ImportError:
        raise SystemExit("請先 pip install google-generativeai")
    genai.configure(api_key=api_key)
    schema = {
        "type": "object",
        "properties": {
            "decisions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "datetime": {"type": "string"},
                        "duration_minutes": {"type": "integer"},
                        "attendees": {"type": "array", "items": {"type": "string"}},
                        "notes": {"type": "string"},
                    },
                    "required": ["title", "datetime"],
                },
            }
        },
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": schema,
        },
    )
    today = date.today().isoformat()
    prompt = (
        f"今天是 {today}（ISO-8601，台灣時區 +08:00）。"
        "從以下會議逐字稿萃取所有『決議』與『待辦』。\n"
        "規則：\n"
        "  (1) 每筆決議含一個工作標題與絕對時間 ISO-8601，沒給時間就略過\n"
        "  (2) attendees 從行文中推得 Email；找不到就空陣列\n"
        "  (3) notes 限 30 字內，只放背景\n"
        "逐字稿：\n" + transcript
    )
    resp = model.generate_content(prompt)
    payload = json.loads(resp.text)
    return payload.get("decisions", [])


def stage4_create_events(decisions: list[dict], dry_run: bool) -> list[str]:
    """Stage 4 — Google Calendar events.insert 帶 attendees[] + extendedProperties.source。
    回傳建出的 event_id 列表；若事件已存在（idempotent by iCalUID）會略過。
    """
    event_ids: list[str] = []
    if dry_run:
        for i, _d in enumerate(decisions):
            event_ids.append(f"dryrun-event-{i:03d}")
        return event_ids
    try:
        from googleapiclient.discovery import build
    except ImportError:
        raise SystemExit("請先 pip install google-api-python-client google-auth")
    creds = _load_calendar_creds()
    service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    for d in decisions:
        digest = hashlib.md5(
            (d.get("title", "") + d.get("datetime", "")).encode()
        ).hexdigest()[:12]
        icaluid = f"meeting-pipeline-{digest}@local"
        existing = service.events().list(
            calendarId="primary",
            iCalUID=icaluid,
            maxResults=1,
        ).execute()
        if existing.get("items"):
            event_ids.append(existing["items"][0]["id"])
            continue
        end_dt = dt.datetime.fromisoformat(d["datetime"]) + dt.timedelta(
            minutes=d.get("duration_minutes", 30)
        )
        body = {
            "summary": d["title"],
            "start": {"dateTime": d["datetime"], "timeZone": "Asia/Taipei"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Taipei"},
            "description": d.get("notes", ""),
            "iCalUID": icaluid,
            "extendedProperties": {"private": {"source": "meeting-pipeline"}},
        }
        attendees = d.get("attendees") or []
        if attendees:
            body["attendees"] = [{"email": e} for e in attendees]
        ev = service.events().insert(
            calendarId="primary", sendUpdates="none", body=body
        ).execute()
        event_ids.append(ev["id"])
    return event_ids


def _load_calendar_creds():
    """優先用 device flow 拿來的 token；缺就退化到 ADC。"""
    token_path = Path(
        os.environ.get("MEETING_PIPELINE_TOKEN", "~/.config/meeting-pipeline/token.json")
    ).expanduser()
    if token_path.exists():
        from google.oauth2.credentials import Credentials

        return Credentials.from_authorized_user_file(str(token_path))
    from google.auth import default

    creds, _ = default(scopes=["https://www.googleapis.com/auth/calendar.events"])
    return creds


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

        print(f"[stage3] 萃取決議中…（dry_run={args.dry_run}）")
        decisions = stage3_extract_decisions(transcript, dry_run=args.dry_run)
        (work_dir / "decisions.json").write_text(
            json.dumps(decisions, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        conn.execute(
            "UPDATE traces SET decisions_json=?, status=?, updated_at=CURRENT_TIMESTAMP WHERE audio_hash=?",
            (json.dumps(decisions, ensure_ascii=False), "parsed", audio_hash),
        )
        conn.commit()
        print(f"[stage3] 解析到 {len(decisions)} 筆決議 → {work_dir/'decisions.json'}")

        print(f"[stage4] 建立行事曆事件中…（dry_run={args.dry_run}）")
        event_ids = stage4_create_events(decisions, dry_run=args.dry_run)
        conn.execute(
            "UPDATE traces SET calendar_event_ids=?, status=?, updated_at=CURRENT_TIMESTAMP WHERE audio_hash=?",
            (json.dumps(event_ids, ensure_ascii=False), "calendared", audio_hash),
        )
        conn.commit()
        print(f"[stage4] 建立 {len(event_ids)} 個 calendar events：{event_ids}")
        print(f"[完成] status=calendared，重跑會跳過")
        return 0
    except Exception as e:
        conn.execute(
            "UPDATE traces SET status='failed', stage=?, error=?, updated_at=CURRENT_TIMESTAMP WHERE audio_hash=?",
            ("stage3+stage4", str(e), audio_hash),
        )
        conn.commit()
        raise
    finally:
        conn.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="會議錄音到行事曆待辦 pipeline")
    ap.add_argument("audio", help="輸入 mp3 / wav / m4a 檔")
    ap.add_argument("--db", default=str(DEFAULT_DB), help="trace DB 路徑")
    ap.add_argument(
        "--work-dir",
        default="~/.local/share/meeting-pipeline",
        help="工作目錄",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="跳過實際 API call，回 mock 結果",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run", help="執行 pipeline").set_defaults(func=cmd_run)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
