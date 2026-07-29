# Prompt Injection Fake Authority

## 說明...
此技能旨在識別和防範偽授權模板的注入攻擊，確保系統不會被惡意指令或偽造的授權請求所影響。

## 關鍵程式碼片段或模式
```javascript
// 檢查授權請求的合法性
function isAuthorizedRequest(request) {
  // 驗證請求來源和內容
  if (validateRequestSource(request) && validateRequestContent(request)) {
    return true;
  }
  return false;
}

// 防止偽授權指令的執行
function sanitizePrompt(prompt) {
  // 移除或轉義潛在的惡意指令
  return prompt.replace(/[^a-zA-Z0-9 ]/g, '');
}
```

## 常見錯誤及避免方法
1. **未驗證請求來源**：未檢查請求的來源是否合法，可能導致偽授權請求被接受。
   - **解決方法**：實施嚴格的來源驗證機制，例如使用數字簽名或令牌。
2. **未過濾惡意內容**：未對輸入內容進行適當的過濾和轉義，可能導致注入攻擊。
   - **解決方法**：對所有輸入進行嚴格的過濾和轉義，移除潛在的惡意指令。
3. **過於寬鬆的授權規則**：授權規則過於寬鬆，可能導致未經授權的操作被執行。
   - **解決方法**：實施最小權限原則，僅允許必要的操作。