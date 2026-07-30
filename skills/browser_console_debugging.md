# Browser Console Debugging

## 說明
瀏覽器控制台是調試前端應用程式的重要工具。此技能涵蓋如何使用瀏覽器控制台來檢查錯誤、日誌記錄和執行調試操作。

## 關鍵代碼片段
```javascript
console.log('User selected:', user);
console.error('An error occurred:', error);

// 評估政策
console.log('Manual policy evaluation:', allowed ? 'ALLOW' : 'DENY');
```

## 常見錯誤及避免方法
1. **控制台日誌過多**：避免在生產環境中留下過多的 `console.log` 調用，這可能會影響性能或洩露敏感信息。
2. **錯誤處理不當**：使用 `try-catch` 塊來捕獲並處理異常，並在控制台中記錄錯誤以幫助調試。
3. **缺乏調試信息**：在調試過程中，確保在控制台中輸出足夠的信息以幫助識別問題。
