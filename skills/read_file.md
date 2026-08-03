# Read File

## 說明
此技能用於從指定路徑讀取文件內容，並將其作為字符串返回。

## 關鍵代碼片段
```python
from pathlib import Path
file_path = '/path/to/file'
content = Path(file_path).read_text()
```

## 常見錯誤及避免方法
- **錯誤**：文件路徑錯誤或文件不存在。
  **解決方法**：在讀取前檢查文件是否存在，或使用異常處理來捕捉錯誤。

- **錯誤**：權限不足導致無法讀取文件。
  **解決方法**：確保運行程序的使用者對目標文件具有讀取權限。