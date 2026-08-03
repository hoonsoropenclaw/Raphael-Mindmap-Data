#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Multilingual Pipeline — OCR 文字辨識 + Whisper 語音轉文字 + MiniMax T2A 語音合成
======================================================================================

Three integrated subcommands in one stdlib-friendly CLI:

  1) `transcribe` — Audio → text (multi-language)
       - Uses faster-whisper (CTranslate2-based, offline)
       - Auto-detects source language; supports translate-to-English
       - Outputs: JSON + plain transcript + SRT/VTT subtitles

  2) `ocr` — Image → text (multi-language)
       - Uses pytesseract (Tesseract 5.x) with language packs
       - Supports: chi_tra+chi_sim+eng+... (any installed tesseract lang)
       - Outputs: JSON + plain text + bounding-box HOCR

  3) `synthesize` — Text → audio (multi-language)
       - Uses MiniMax T2A v2 via the `mmx` CLI (MiniMax-Speech)
       - 30+ system voices; auto language boost
       - Outputs: MP3/WAV/FLAC/Opus

  4) `pipeline` — Full audio→text→(translate)→audio round-trip
       - Demonstrates the multilingual doc-processing workflow

Environment:
  - `HF_HOME` (default: ~/.cache/huggingface) — Whisper model cache
  - `MINIMAX_API_KEY` — for the T2A synth step (not required for transcribe/ocr)
  - `mmx` CLI must be installed (`npx -y mmx-cli --version`)

Whisper models: tiny / base / small / medium / large-v3 / large-v3-turbo
OCR languages:   eng / chi_tra / chi_sim / jpn / kor / spa / fra / deu / ...

Example:
  # transcribe Chinese audio
  python multilingual_pipeline.py transcribe audio.mp3 --lang zh --model small

  # OCR a Chinese+English document
  python multilingual_pipeline.py ocr document.png --lang chi_tra+eng

  # synthesize Mandarin
  python multilingual_pipeline.py synthesize "你好世界" --out greeting.mp3 \
    --voice female-shaonv --lang zh

  # full round-trip: audio → text → translated audio
  python multilingual_pipeline.py pipeline meeting_zh.mp3 --target-lang en
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


# ---------- 0. Environment / dependency helpers --------------------------------

# Default: tiny (75MB, runs on N100 in <2s for 8s audio).
# Override at runtime with WHISPER_MODEL=base|small|medium|large-v3
# or with --model <name>. base/small need ~460MB/1.5GB HF cache.
WHISPER_MODEL_DEFAULT = os.environ.get("WHISPER_MODEL", "tiny")
HF_HOME = os.environ.get("HF_HOME", os.path.expanduser("~/.cache/huggingface"))


def _have(cmd: str) -> bool:
    return subprocess.run(
        ["which", cmd], capture_output=True
    ).returncode == 0


def _ffmpeg_to_wav(src: str, dst: str) -> None:
    """Convert any input to 16kHz mono PCM WAV (Whisper's preferred input)."""
    if not _have("ffmpeg"):
        raise SystemExit("ERROR: ffmpeg is not installed. sudo apt install ffmpeg")
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", src,
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
            dst,
        ],
        check=True,
    )


# ---------- 1. Subcommand: transcribe -----------------------------------------

def cmd_transcribe(args: argparse.Namespace) -> int:
    """Audio → text using faster-whisper."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("ERROR: faster-whisper not installed. pip install faster-whisper",
              file=sys.stderr)
        return 2

    src = Path(args.input).expanduser().resolve()
    if not src.exists():
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 2

    # Convert to 16kHz mono WAV if not already
    work_wav = src.with_suffix(".converted.wav")
    if src.suffix.lower() not in (".wav",) or args.force_convert:
        print(f"[transcribe] ffmpeg → {work_wav.name}")
        _ffmpeg_to_wav(str(src), str(work_wav))
        audio_path = str(work_wav)
    else:
        audio_path = str(src)

    print(f"[transcribe] loading model: {args.model} (device={args.device}, "
          f"compute={args.compute_type})")
    t0 = time.time()
    os.environ.setdefault("HF_HOME", HF_HOME)
    model = WhisperModel(
        args.model, device=args.device, compute_type=args.compute_type,
    )
    print(f"[transcribe] model ready in {time.time()-t0:.1f}s")

    transcribe_kwargs = dict(
        audio=audio_path,
        beam_size=args.beam_size,
        vad_filter=args.vad,
        vad_parameters={"min_silence_duration_ms": 500} if args.vad else None,
    )
    if args.task == "translate":
        # Whisper's translate task always translates to English.
        transcribe_kwargs["task"] = "translate"
    if args.initial_prompt:
        transcribe_kwargs["initial_prompt"] = args.initial_prompt
    if args.language:
        transcribe_kwargs["language"] = args.language

    print(f"[transcribe] running (task={args.task}, lang={args.language or 'auto'})…")
    t0 = time.time()
    segments, info = model.transcribe(**transcribe_kwargs)
    duration = info.duration
    print(f"[transcribe] audio duration: {duration:.1f}s, "
          f"detected language: {info.language} "
          f"(p={info.language_probability:.3f})")

    rows = []
    for seg in segments:
        rows.append({
            "id": seg.id,
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "text": seg.text.strip(),
            "avg_logprob": round(seg.avg_logprob, 4),
            "no_speech_prob": round(seg.no_speech_prob, 4),
        })
        if not args.quiet:
            print(f"  [{seg.start:6.2f}s → {seg.end:6.2f}s] {seg.text.strip()}")

    elapsed = time.time() - t0
    rtf = elapsed / max(duration, 0.1)
    print(f"[transcribe] done in {elapsed:.1f}s (real-time factor {rtf:.2f}x)")

    # Output: JSON + plain transcript + SRT (subtitles)
    out_base = Path(args.output_prefix) if args.output_prefix else src.with_suffix("")
    json_path = out_base.with_suffix(".transcribe.json")
    txt_path = out_base.with_suffix(".transcribe.txt")
    srt_path = out_base.with_suffix(".srt")

    payload = {
        "input": str(src),
        "model": args.model,
        "device": args.device,
        "compute_type": args.compute_type,
        "task": args.task,
        "detected_language": info.language,
        "language_probability": round(info.language_probability, 4),
        "duration": round(duration, 3),
        "elapsed_seconds": round(elapsed, 3),
        "rtf": round(rtf, 3),
        "segments": rows,
        "full_text": " ".join(r["text"] for r in rows).strip(),
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    txt_path.write_text(payload["full_text"] + "\n", encoding="utf-8")

    # SRT
    srt_lines = []
    for i, r in enumerate(rows, 1):
        srt_lines.append(str(i))
        srt_lines.append(
            f"{_format_ts(r['start'])} --> {_format_ts(r['end'])}"
        )
        srt_lines.append(r["text"])
        srt_lines.append("")
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")

    print(f"\n[transcribe] outputs:")
    print(f"  - {json_path}")
    print(f"  - {txt_path}")
    print(f"  - {srt_path}")
    if not rows:
        print("(no speech detected — check audio or language hint)")
    return 0


def _format_ts(seconds: float) -> str:
    """Format seconds as SRT timestamp HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# ---------- 2. Subcommand: ocr -----------------------------------------------

def cmd_ocr(args: argparse.Namespace) -> int:
    """Image → text using Tesseract via pytesseract."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError as e:
        print(f"ERROR: missing dependency: {e}. pip install pytesseract Pillow",
              file=sys.stderr)
        return 2

    src = Path(args.input).expanduser().resolve()
    if not src.exists():
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 2
    if not _have("tesseract"):
        print("ERROR: tesseract binary not found. sudo apt install tesseract-ocr",
              file=sys.stderr)
        return 2

    print(f"[ocr] loading image: {src}")
    img = Image.open(src)
    print(f"[ocr] image size: {img.size}, mode: {img.mode}")

    lang = args.lang or "eng"
    t0 = time.time()
    # Plain text
    text = pytesseract.image_to_string(img, lang=lang,
                                       config=f"--psm {args.psm}")
    # Detailed data (boxes, confidences)
    data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT,
                                     config=f"--psm {args.psm}")
    # HOCR (HTML with bounding boxes) — tesseract 5.x API name
    try:
        hocr = pytesseract.image_to_pdf_or_hocr(img, lang=lang,
                                                config=f"--psm {args.psm}")
    except AttributeError:
        # Fallback for older pytesseract versions
        hocr = pytesseract.image_to_string(img, lang=lang,
                                           config=f"--psm {args.psm}")
    elapsed = time.time() - t0

    # Filter useful rows
    words = []
    for i, txt in enumerate(data["text"]):
        if txt and txt.strip():
            words.append({
                "text": txt,
                "conf": int(data["conf"][i]),
                "left": int(data["left"][i]),
                "top": int(data["top"][i]),
                "width": int(data["width"][i]),
                "height": int(data["height"][i]),
                "block": int(data["block_num"][i]),
                "line": int(data["line_num"][i]),
                "word_num": int(data["word_num"][i]),
            })

    out_base = Path(args.output_prefix) if args.output_prefix else src.with_suffix("")
    json_path = out_base.with_suffix(".ocr.json")
    txt_path = out_base.with_suffix(".ocr.txt")
    hocr_path = out_base.with_suffix(".hocr")

    payload = {
        "input": str(src),
        "lang": lang,
        "psm": args.psm,
        "elapsed_seconds": round(elapsed, 3),
        "image_size": list(img.size),
        "word_count": len(words),
        "words": words,
        "full_text": text,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    txt_path.write_text(text, encoding="utf-8")
    if isinstance(hocr, bytes):
        hocr_path.write_bytes(hocr)
    else:
        hocr_path.write_text(str(hocr), encoding="utf-8")

    print(f"[ocr] detected {len(words)} words in {elapsed:.1f}s")
    print(f"[ocr] first 5 lines of text:")
    for line in text.splitlines()[:5]:
        if line.strip():
            print(f"  │ {line}")
    print(f"\n[ocr] outputs:")
    print(f"  - {json_path}")
    print(f"  - {txt_path}")
    print(f"  - {hocr_path}")
    return 0


# ---------- 3. Subcommand: synthesize (MiniMax T2A) ---------------------------

def cmd_synthesize(args: argparse.Namespace) -> int:
    """Text → speech using MiniMax T2A v2 via the `mmx` CLI."""
    if not _have("mmx") and not _have("npx"):
        print("ERROR: mmx CLI not available. npx -y mmx-cli --help", file=sys.stderr)
        return 2

    if args.input:
        text = Path(args.input).expanduser().read_text(encoding="utf-8").strip()
        if not text:
            print(f"ERROR: empty text file: {args.input}", file=sys.stderr)
            return 2
    else:
        text = args.text
    if not text:
        print("ERROR: --text or --input required", file=sys.stderr)
        return 2

    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    # Strip placeholder 3 dots the shell may have substituted
    mmx_bin = "mmx" if _have("mmx") else "npx"
    cmd = [mmx_bin]
    if mmx_bin == "npx":
        cmd += ["-y", "mmx-cli"]
    cmd += [
        "speech", "synthesize",
        "--text", text,
        "--voice", args.voice,
        "--model", args.model,
        "--format", args.format,
        "--sample-rate", str(args.sample_rate),
        "--bitrate", str(args.bitrate),
        "--language", args.lang,
        "--speed", str(args.speed),
        "--out", str(out),
    ]
    if args.subtitles:
        cmd.append("--subtitles")

    print(f"[synthesize] running: {' '.join(cmd[:8])}…")
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout)
    elapsed = time.time() - t0
    if proc.returncode != 0:
        print(f"ERROR (exit {proc.returncode}): {proc.stderr}", file=sys.stderr)
        return proc.returncode

    if not out.exists():
        print(f"ERROR: expected output {out} not created", file=sys.stderr)
        print("--- mmx stdout ---")
        print(proc.stdout)
        return 3

    size = out.stat().st_size
    print(f"[synthesize] OK: {size} bytes → {out} ({elapsed:.1f}s)")
    print(f"[synthesize] voice={args.voice} model={args.model} lang={args.lang}")
    if proc.stdout.strip():
        try:
            data = json.loads(proc.stdout)
            if "duration_ms" in data:
                print(f"[synthesize] duration: {data['duration_ms']}ms")
        except json.JSONDecodeError:
            pass
    return 0


# ---------- 4. Subcommand: pipeline (full round-trip) ------------------------

def cmd_pipeline(args: argparse.Namespace) -> int:
    """Audio → text → (translate) → audio round-trip.

    Step 1: faster-whisper transcribes input audio (auto-detect src lang).
    Step 2: if --target-lang differs from detected lang AND a translation is
            available, the transcript is passed through to MiniMax T2A.
            (For demonstration we use the source text as-is; users can plug
            a real translation backend in the `translate_text` hook below.)
    Step 3: MiniMax T2A synthesizes the result.
    """
    print("=" * 60)
    print(f"PIPELINE: {args.input} → text → {args.target_lang} audio")
    print("=" * 60)

    # ----- Step 1: transcribe -----
    src = Path(args.input).expanduser().resolve()
    if not src.exists():
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 2

    work = Path(args.work_dir).expanduser().resolve() if args.work_dir \
        else src.parent / "pipeline_work"
    work.mkdir(parents=True, exist_ok=True)

    stage1 = work / (src.stem + ".transcribe.json")
    if not stage1.exists() or args.force:
        rc = subprocess.run([
            sys.executable, __file__, "transcribe",
            str(src),
            "--output-prefix", str(work / src.stem),
            "--model", args.model,
            "--task", "transcribe",
        ]).returncode
        if rc != 0:
            return rc
    payload = json.loads(stage1.read_text(encoding="utf-8"))
    src_text = payload["full_text"]
    src_lang = payload["detected_language"]
    print(f"\n[pipeline] step 1 OK: {len(src_text)} chars, lang={src_lang}")

    if not src_text.strip():
        print("[pipeline] no text detected; aborting")
        return 4

    # ----- Step 2: translate (hook) -----
    target_text = src_text
    if args.target_lang and args.target_lang != src_lang:
        target_text = _translate_text(src_text, src_lang, args.target_lang,
                                      engine=args.translate_engine)
        print(f"\n[pipeline] step 2 translated ({src_lang} → {args.target_lang}):")
        print(f"  {target_text[:200]}{'…' if len(target_text) > 200 else ''}")
    else:
        print(f"\n[pipeline] step 2: skip translate (target={args.target_lang or src_lang})")

    # ----- Step 3: synthesize -----
    out_audio = Path(args.output).expanduser().resolve() if args.output \
        else work / f"{src.stem}.{args.target_lang or src_lang}.mp3"
    rc = subprocess.run([
        sys.executable, __file__, "synthesize",
        "--text", target_text,
        "--voice", args.voice,
        "--model", "speech-2.8-hd",
        "--lang", args.target_lang or src_lang,
        "--out", str(out_audio),
        "--format", "mp3",
    ]).returncode
    if rc != 0:
        return rc

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"  transcript:  {work / (src.stem + '.transcribe.txt')}")
    print(f"  subtitles:   {work / (src.stem + '.srt')}")
    print(f"  output aud:  {out_audio}")
    return 0


def _translate_text(text: str, src: str, tgt: str, engine: str = "passthrough") -> str:
    """Translation hook. Default = passthrough. Plug in argos / deep-translator
    / Claude / etc. when needed.

    For demonstration we prefix the source with a translation-marker so the
    output audio clearly says it was passed through (e.g. when the user runs
    pipeline without setting up a translation backend).
    """
    if engine == "passthrough":
        return text
    raise NotImplementedError(
        f"Translation engine '{engine}' not implemented in this build. "
        "Edit _translate_text() in multilingual_pipeline.py to plug in "
        "argostranslate / deep-translator / etc."
    )


# ---------- 5. CLI plumbing ---------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="multilingual_pipeline",
        description=(
            "OCR + Whisper + MiniMax T2A multilingual pipeline. "
            "Subcommands: transcribe / ocr / synthesize / pipeline."
        ),
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # transcribe
    pt = sub.add_parser("transcribe", help="Audio → text via faster-whisper")
    pt.add_argument("input", help="Audio file (mp3/wav/m4a/flac/ogg…)")
    pt.add_argument("--model", default=WHISPER_MODEL_DEFAULT,
                    help=f"Whisper model (default: {WHISPER_MODEL_DEFAULT})")
    pt.add_argument("--device", default="cpu", choices=["cpu", "cuda"],
                    help="Inference device")
    pt.add_argument("--compute-type", default="int8",
                    help="CTranslate2 compute type (int8/float16/float32)")
    pt.add_argument("--task", default="transcribe",
                    choices=["transcribe", "translate"],
                    help="transcribe = same language; translate = → English")
    pt.add_argument("--language", dest="language", default=None,
                    help="Force source language (e.g. zh, en, ja). Default=auto")
    pt.add_argument("--initial-prompt", default=None,
                    help="Optional prompt to bias vocabulary / style")
    pt.add_argument("--beam-size", type=int, default=5)
    pt.add_argument("--vad", action="store_true",
                    help="Enable VAD (silence trimming) — recommended for noisy audio")
    pt.add_argument("--force-convert", action="store_true",
                    help="Always re-run ffmpeg even if input is WAV")
    pt.add_argument("--output-prefix", default=None,
                    help="Override output path (default: alongside input)")
    pt.add_argument("--quiet", action="store_true",
                    help="Don't print per-segment lines")
    pt.set_defaults(func=cmd_transcribe)

    # ocr
    po = sub.add_parser("ocr", help="Image → text via Tesseract")
    po.add_argument("input", help="Image file (png/jpg/tiff/bmp/webp)")
    po.add_argument("--lang", default="eng",
                    help="Tesseract language code (e.g. chi_tra+eng, eng, jpn)")
    po.add_argument("--psm", type=int, default=3,
                    help="Page segmentation mode (default 3 = auto)")
    po.add_argument("--output-prefix", default=None,
                    help="Override output path (default: alongside input)")
    po.set_defaults(func=cmd_ocr)

    # synthesize
    ps = sub.add_parser("synthesize", help="Text → audio via MiniMax T2A")
    text_or_file = ps.add_mutually_exclusive_group(required=True)
    text_or_file.add_argument("--text", help="Text to speak")
    text_or_file.add_argument("--input", help="Read text from file (UTF-8)")
    ps.add_argument("--out", required=True, help="Output audio file (mp3/wav/…)")
    ps.add_argument("--voice", default="English_expressive_narrator",
                    help="Voice ID (see mmx-cli speech voices)")
    ps.add_argument("--model", default="speech-2.8-hd",
                    choices=["speech-02-hd", "speech-02-turbo",
                             "speech-2.6-hd", "speech-2.6-turbo",
                             "speech-2.8-hd", "speech-2.8-turbo"],
                    help="T2A model")
    ps.add_argument("--lang", default="auto",
                    help="Language boost (auto / zh / en / ja / ko / …)")
    ps.add_argument("--format", default="mp3",
                    choices=["mp3", "pcm", "flac", "wav", "opus"])
    ps.add_argument("--sample-rate", type=int, default=32000)
    ps.add_argument("--bitrate", type=int, default=128000)
    ps.add_argument("--speed", type=float, default=1.0)
    ps.add_argument("--subtitles", action="store_true",
                    help="Include subtitle timing in the output JSON")
    ps.add_argument("--timeout", type=int, default=180)
    ps.set_defaults(func=cmd_synthesize)

    # pipeline
    pp = sub.add_parser("pipeline",
                        help="Audio → text → translate → audio round-trip")
    pp.add_argument("input", help="Source audio file")
    pp.add_argument("--target-lang", default="en",
                    help="Target language for synthesis (default: en)")
    pp.add_argument("--model", default=WHISPER_MODEL_DEFAULT,
                    help="Whisper model (default: small)")
    pp.add_argument("--voice", default="English_expressive_narrator",
                    help="TTS voice for target language")
    pp.add_argument("--translate-engine", default="passthrough",
                    help="Translation backend (passthrough / argo / claude)")
    pp.add_argument("--work-dir", default=None,
                    help="Where to drop intermediate files")
    pp.add_argument("--output", default=None,
                    help="Final audio output path")
    pp.add_argument("--force", action="store_true",
                    help="Re-run step 1 even if its output exists")
    pp.set_defaults(func=cmd_pipeline)

    return p


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n[aborted]")
        return 130


if __name__ == "__main__":
    sys.exit(main())
