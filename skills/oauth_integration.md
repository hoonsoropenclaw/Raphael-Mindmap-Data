# OAuth Integration

## 說明...
該技能涉及實現 OAuth 認證流程，包括 Web Server Flow 和 Device Code Flow，以確保應用程序能夠安全地訪問用戶的 Google Calendar 數據。

## 關鍵代碼片段或模式
```python
from calendar_reminder.auth import run_oauth_web, run_oauth_device
# Web Server Flow
run_oauth_web('~/.hermes/google_client_secret.json', ['https://www.googleapis.com/auth/calendar'], token_path='~/.hermes/calendar_tokens.json')
# Device Code Flow
print('user_code 請到 https://www.google.com/device 輸入')
run_oauth_device('~/.hermes/google_client_secret.json', ['https://www.googleapis.com/auth/calendar'], token_path='~/.hermes/calendar_tokens.json')
```

## 常見錯誤及避免方法
- **錯誤**: OAuth 認證流程中斷，導致無法獲取訪問令牌。
  **避免方法**: 確保應用程序在整個認證流程中正確處理所有可能的錯誤情況。
- **錯誤**: 訪問令牌過期，導致應用程序無法訪問數據。
  **避免方法**: 實現令牌刷新機制，確保應用程序始終擁有有效的訪問令牌。