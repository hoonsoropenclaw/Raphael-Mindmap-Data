# Fixture Mode Management

## 說明...
該技能涉及使用預定義的測試數據（fixtures）來模擬真實數據源，確保在離線環境下進行測試時應用程序的穩定性。

## 關鍵代碼片段或模式
```bash
export CALENDAR_REMINDER_FIXTURE_PATH=/tmp/cal_e2e_web2.json
# 啟動應用程序並使用 fixture
exec uvicorn calendar_reminder.web:app --host 127.0.0.1 --port 8766 --log-level warning
```

## 常見錯誤及避免方法
- **錯誤**: fixture 文件格式錯誤，導致應用程序無法正確解析數據。
  **避免方法**: 確保 fixture 文件的格式與應用程序預期的格式一致，並在測試前進行驗證。
- **錯誤**: 應用程序在離線模式下無法正常運行。
  **避免方法**: 檢查應用程序的配置，確保在離線模式下正確加載 fixture 文件。