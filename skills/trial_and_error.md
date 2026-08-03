# Trial and Error Skill

## 說明...
試誤學習是一種通過不斷嘗試和錯誤來解決問題的方法。此技能涉及在遇到錯誤時自動調試、識別問題根源並實施解決方案。

## 關鍵代碼片段或模式
```python
# Example of a simple retry mechanism
import time

def retry(func, retries=5, delay=2):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            print(f'Error: {e}, retrying...')
            time.sleep(delay)
    raise Exception('Max retries exceeded')
```

## 常見錯誤及避免方法
- **錯誤**：無限循環導致程序掛起。
  **解決方法**：設置最大重試次數和每次重試之間的延遲，避免無限循環。