# PDF and OCR Advanced Processing

## 說明...
此技能結合 PyMuPDF、Tesseract、regex 等技術，實現對 PDF 文件的自動化處理，包括文字層提取、OCR 識別、欄位萃取等。

## 關鍵代碼片段或模式
```python
def process_pdf(file_path):
    # 使用 PyMuPDF 提取文字層
    text = extract_text_with_pymupdf(file_path)
    if not text:
        # 如果文字層為空，則使用 OCR 識別
        text = perform_ocr(file_path)
    # 使用 regex 萃取欄位
    fields = extract_fields_with_regex(text)
    return fields
```

## 常見錯誤及避免方法
- **錯誤**: OCR 識別錯誤導致欄位萃取失敗。
  **解決方法**: 優化 OCR 參數，如 DPI、語言包等，並使用後處理規則修正常見錯誤。
- **錯誤**: 欄位萃取規則不夠靈活。
  **解決方法**: 使用正則表達式的命名捕獲組，並允許可選的分隔符和格式。