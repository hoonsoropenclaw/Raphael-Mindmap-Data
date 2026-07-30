# Google Calendar Integration

## 說明...
此微技能提供與 Google Calendar API 的整合功能，包括事件讀取、OAuth 認證以及日曆事件解析。

## 關鍵代碼片段
```python
def fetch_google_calendar_events(calendar_id, token_path):
    # 使用 OAuth 認證並調用 Google Calendar API
    ...
    return events
```

## 常見錯誤與解決方法
- **OAuth 未完成或 token 過期**：確保 token 路徑正確並且 token 有效。可以在初始化時檢查 token 是否存在並且未過期。
- **API 調用失敗**：處理網絡錯誤或 API 限流問題，添加重試機制。