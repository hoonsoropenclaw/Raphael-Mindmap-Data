# Baseline Management with Fingerprinting

## 說明
在視覺回歸測試中，基準圖像（baseline）的管理和驗證是關鍵環節。使用指紋（如 SHA-256）來標識和管理基準圖像，可以確保每次測試時比對的是正確的圖像。

## 關鍵代碼片段
```python
from hashlib import sha256

def fingerprint(file_path):
    with open(file_path, 'rb') as f:
        return sha256(f.read()).hexdigest()

# 驗證基準圖像
baseline_fingerprint = fingerprint(baseline_path)
current_fingerprint = fingerprint(current_path)
if baseline_fingerprint != current_fingerprint:
    # 執行像素比對
    mismatch = pixelmatch.pixelmatch(...)
```

## 常見錯誤及避免方法
- **錯誤**: 基準圖像指紋不匹配，但實際上圖像內容未改變。
  - **解決方法**: 確保在生成指紋之前，圖像文件已正確寫入並刷新緩存。
- **錯誤**: 基準圖像未正確存儲或讀取，導致比對失敗。
  - **解決方法**: 檢查文件路徑和權限，確保基準圖像能夠被正確讀取和寫入。