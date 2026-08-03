# Trial and Error Skill

## 說明...
在自動化任務中，經常需要通過不斷嘗試和修正來解決問題。本技能涉及如何識別錯誤、嘗試不同的解決方案以及驗證修正效果。

## 關鍵代碼片段或模式
```javascript
function attemptFix(error) {
  if (error.includes('timeout')) {
    // 增加超時時間
    return { action: 'increase_timeout', value: 5000 };
  } else if (error.includes('not found')) {
    // 檢查文件路徑
    return { action: 'check_file_path', value: '/path/to/file' };
  }
  // 其他錯誤處理
}

try {
  // 執行操作
} catch (error) {
  const fix = attemptFix(error.message);
  // 執行修正操作
}
```

## 常見錯誤及避免方法
- **錯誤**：無限修正導致無限循環。
  **解決方法**：設置最大嘗試次數或使用指數退避策略來限制修正嘗試的頻率。