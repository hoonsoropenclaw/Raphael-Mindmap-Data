# State Change Authorization

## 說明...
此技能根據 HTTP 方法（如 POST、PUT、PATCH、DELETE）自動推斷是否允許狀態變更操作。默認情況下，POST/PUT/PATCH/DELETE 被視為狀態變更操作，需要通過 `--allow-state-changes` 標誌來啟用。

## 關鍵代碼片段或模式
```python
inferred_state_change = method in {"POST", "PUT", "PATCH", "DELETE"} or destructive
state_changing = payload.get("state_changing", inferred_state_change)
```

## 常見錯誤及避免方法
- **錯誤**：忘記標記狀態變更操作，導致安全閘門阻止操作。
  **解決方法**：確保在執行狀態變更操作時使用 `--allow-state-changes` 標誌，或者在 payload 中明確設置 `state_changing` 為 `True`。
- **錯誤**：將非狀態變更方法（如 GET）錯誤地標記為狀態變更。
  **解決方法**：僅將 POST、PUT、PATCH、DELETE 標記為狀態變更，避免誤標其他方法。