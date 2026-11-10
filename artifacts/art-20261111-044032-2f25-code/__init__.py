"""xlsx_recon — 資料夾內多個 Excel 的合併與對帳工具。

用法：
    python -m xlsx_recon --input ./資料夾 --out-dir ./輸出
    python -m xlsx_recon --input ./資料夾 --dry-run
    python -m xlsx_recon --input ./資料夾 --report-only --json
"""
from __future__ import annotations

from .cli import build_parser, main

__all__ = ["main", "build_parser", "__version__"]

__version__ = "1.0.0"
