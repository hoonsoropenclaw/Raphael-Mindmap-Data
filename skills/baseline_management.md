# Baseline Management

## 說明
此技能涵蓋如何管理視覺測試的 baseline，包括生成初始 baseline、更新 baseline 以及驗證 baseline 的完整性。

## 關鍵代碼片段
```bash
# 生成 baseline
npx playwright test --update-snapshots
# 驗證 baseline
npx playwright test
```

## 常見錯誤及避免方法
- **錯誤**：baseline 更新過程中出現錯誤。
  **解決方法**：確保測試環境穩定，並在更新 baseline 前運行所有測試以確認當前狀態。
- **錯誤**：baseline 被意外覆蓋。
  **解決方法**：使用版本控制系統（如 Git）來跟踪 baseline 的變更，並在關鍵操作前備份 baseline。