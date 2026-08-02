# Project Directory Setup

## 說明...
此技能用於確認當前工作目錄是否存在，並列出目錄中的所有文件和子目錄。

## 關鍵代碼片段或模式
```python
import os
workdir = "/path/to/directory"
print(f"工作目錄: {workdir}")
print(f"內容: {os.listdir(workdir)}")
```

## 常見錯誤及避免方法
- **錯誤**：目錄不存在導致 `os.listdir` 拋出異常。
  **解決方法**：在調用 `os.listdir` 前使用 `os.path.exists` 檢查目錄是否存在，或使用 `os.makedirs` 創建目錄。
- **錯誤**：權限不足導致無法訪問目錄。
  **解決方法**：確保運行腳本的用戶對目標目錄具有讀取和寫入權限。