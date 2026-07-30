# Prompt Injection Fake Authority Detection

## 說明...
此技能旨在識別和防範基於偽造權限的 prompt injection 攻擊。

## 關鍵代碼片段或模式
```python
# 檢查關鍵詞和模式
if any(keyword in message for keyword in ['極限超頻模式', 'FULL AUTONOMY', '嚴格禁止使用']):
    # 驗證授權依據
    if not validate_authority(message):
        raise PermissionError('Unauthorized access attempt detected.')
```

## 常見錯誤及避免方法
- **錯誤**：未驗證關鍵詞的上下文，導致誤判或漏判。
  **解決方法**：使用正則表達式或自然語言處理技術來更準確地識別攻擊模式。
- **錯誤**：過於嚴格地阻止所有可疑請求，影響正常操作。
  **解決方法**：設置合理的閾值和例外規則，確保在不影響安全性的前提下允許合法請求。