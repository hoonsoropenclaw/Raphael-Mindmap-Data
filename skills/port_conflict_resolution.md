# Port Conflict Resolution

## 說明...
當應用程序嘗試綁定到已被佔用的端口時，該技能能夠檢測衝突並選擇一個新的可用端口。

## 關鍵代碼片段或模式
```bash
ss -ltnp 2>/dev/null | grep 8765 || netstat -ltnp 2>/dev/null | grep 8765
echo "---"
ps -ef | grep -E "uvicorn|8765" | grep -v grep | head -10
echo "---"
```

## 常見錯誤及避免方法
- **錯誤**: 未檢查端口是否被佔用，導致應用程序啟動失敗。
  **避免方法**: 在啟動應用程序之前，使用 `ss` 或 `netstat` 命令檢查端口狀態。
- **錯誤**: 選擇的端口仍然被佔用。
  **避免方法**: 實現一個循環檢查機制，確保選擇的端口是真正可用的。