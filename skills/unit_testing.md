# Unit Testing

## 說明...
### 目的
為各模組編寫單元測試，確保功能正確性並捕捉潛在錯誤。

### 關鍵代碼片段
```python
def test_ocr_engine():
    make_test_png('/tmp/test_ocr.png')
    engine = get_default_engine()
    r = engine.ocr_file('/tmp/test_ocr.png')
    assert 'Hello' in r.text
    assert r.confidence > 50
    assert len(r.bboxes) >= 2
```

### 常見錯誤及避免方法
- **錯誤**：測試環境設置錯誤，導致測試結果不準確。
  **避免方法**：確保測試環境與實際運行環境一致，例如使用相同的庫版本和配置。

- **錯誤**：測試覆蓋率不足，導致潛在錯誤未被發現。
  **避免方法**：編寫全面的測試用例，覆蓋各種可能的輸入和邊界條件。