# Google Calendar API Integration

## 說明...
此微技能涵蓋如何初始化 Google Calendar API、處理 OAuth 驗證流程，以及使用 API 進行事件的新增、刪除、查詢和更新操作。

## 關鍵程式碼片段或模式
```javascript
async function initializeCalendarAPI() {
  const auth = new google.auth.GoogleAuth({
    keyFile: 'path/to/credentials.json',
    scopes: ['https://www.googleapis.com/auth/calendar'],
  });
  googleCalendar = google.calendar({ version: 'v3', auth });
}

async function listEvents() {
  const res = await googleCalendar.events.list({
    calendarId: 'primary',
    timeMin: (new Date()).toISOString(),
    maxResults: 10,
    singleEvents: true,
    orderBy: 'startTime',
  });
  return res.data.items;
}
```

## 常見錯誤及避免方法
- **OAuth 驗證失敗**：確保 `credentials.json` 路徑正確，且 OAuth 憑證已正確設置。
- **權限不足**：確認應用程式已獲得所需的 API 權限，例如 `https://www.googleapis.com/auth/calendar`。
- **時間格式錯誤**：使用 ISO 格式的日期時間字符串，避免因格式問題導致請求失敗。