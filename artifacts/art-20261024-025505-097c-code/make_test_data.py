#!/usr/bin/env python3
"""產生測試用的 Excel 資料（涵蓋正常、空資料、異常格式三類情境）。

執行：python make_test_data.py
產出：
  test_data/          正常情境：2 個檔案、欄位不齊（測欄位聯集）、含退款/負值
  test_data_empty/    空資料夾情境（另外放一個 0 欄位的 xlsx）
  test_data_bad/      異常格式：損毀的 xlsx（不是真的 zip）、密碼保護模擬、純文字偽裝成 xlsx
"""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from openpyxl import Workbook

HERE = Path(__file__).resolve().parent


def make_normal() -> Path:
    """正常情境：兩個檔案，欄位不齊，第二個有退款與負值。"""
    d = HERE / "test_data"
    d.mkdir(parents=True, exist_ok=True)

    # 檔案 A：兩個分頁
    wb = Workbook()
    ws = wb.active
    ws.title = "一月"
    ws.append(["單號", "處室", "金額", "數量"])
    ws.append(["A001", "總務處", 1200, 3])
    ws.append(["A002", "人事室", 800, 1])
    ws.append(["A003", "總務處", 450, 2])

    ws2 = wb.create_sheet("二月")
    ws2.append(["單號", "處室", "金額", "數量"])
    ws2.append(["B001", "財務室", 2000, 5])
    ws2.append(["B002", "人事室", 650, 1])
    wb.save(d / "2026-01_2月經費.xlsx")

    # 檔案 B：欄位不齊（多了 部門欄，少了 數量）+ 退款列 + 負值
    wb2 = Workbook()
    ws = wb2.active
    ws.title = "三月"
    ws.append(["單號", "處室", "金額", "部門", "備註"])
    ws.append(["C001", "教務組", 1500, "高中部", "正常"])
    ws.append(["C002", "教務組", -300, "高中部", "退款"])
    ws.append(["C003", "總務處", 99, "國中部", "折扣"])
    wb2.save(d / "2026-03_3月經費.xlsx")
    return d


def make_empty() -> Path:
    """空資料情境：一個欄位為零列的 xlsx + 空資料夾。"""
    d = HERE / "test_data_empty"
    d.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "空"
    ws.append(["單號", "金額"])  # 只有表頭、零資料列
    wb.save(d / "只有表頭.xlsx")
    return d


def make_bad() -> Path:
    """異常格式：損毀檔、文字偽裝、密碼保護（zip 加密的近似：不加密但標記）。"""
    d = HERE / "test_data_bad"
    d.mkdir(parents=True, exist_ok=True)

    # 1. 損毀的 xlsx（純文字內容，不是真的 zip）
    (d / "損毀的檔案.xlsx").write_text("這個檔案看起來是 xlsx，但其實是純文字。\n", encoding="utf-8")

    # 2. 偽裝：實際是舊格式 .xls 的位元組，副檔名改成 .xlsx
    (d / "偽裝成xlsx的舊檔.xlsx").write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 64)

    # 3. 密碼保護的 xlsx（近似模擬：真實加密需外部套件，這裡做「開啟會失敗」的驗證檔）
    p = d / "密碼保護.xlsx"
    p.write_bytes(b"PK\x03\x04" + b"\x00" * 128)
    return d


if __name__ == "__main__":
    for target in (HERE / "test_data", HERE / "test_data_empty", HERE / "test_data_bad"):
        if target.exists():
            shutil.rmtree(target)
    print("正常情境 →", make_normal())
    print("空資料情境 →", make_empty())
    print("異常格式情境 →", make_bad())
    print("完成")
