# Background Process Management

## 說明...
該技能涉及啟動後台進程、停止現有進程以及檢查進程狀態以確保應用程序正常運行。

## 關鍵代碼片段或模式
```bash
ps aux | grep -E "uvicorn calendar_reminder" | grep -v grep
process_id="proc_b36caaa6142e"
echo "---"
ss -ltn 2>/dev/null | grep -E "87(65|66|67|68|69|70)"
```

## 常見錯誤及避免方法
- **錯誤**: 嘗試停止不存在的進程，導致錯誤訊息。
  **避免方法**: 在停止進程之前，先檢查進程是否存在。
- **錯誤**: 進程無法正常停止。
  **避免方法**: 使用 `kill` 命令並確保具有足夠的權限。