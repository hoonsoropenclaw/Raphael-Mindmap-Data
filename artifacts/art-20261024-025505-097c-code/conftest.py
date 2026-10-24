"""pytest 設定：自動產生測試資料。

為什麼需要這個檔案（2026-10-24 evaluate 抓到）：
原本三組測試資料（test_data/ test_data_empty/ test_data_bad/）是手動執行
`python make_test_data.py` 產生的，沒有交付到作品目錄。
結果：在交付目錄直接跑 `pytest` → 12 failed / 24 passed（假綠燈）。

修法：把產生流程做成 session-scoped autouse fixture，
任何乾淨環境 clone 後直接 `pytest -q` 就全綠，不需要先手動執行任何指令。
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import make_test_data  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _generate_test_data():
    """在測試開始前自動產生三組測試資料（冪等：已存在則重建）。"""
    for target in (
        HERE / "test_data",
        HERE / "test_data_empty",
        HERE / "test_data_bad",
    ):
        if target.exists():
            import shutil

            shutil.rmtree(target)
    make_test_data.make_normal()
    make_test_data.make_empty()
    make_test_data.make_bad()
    yield
