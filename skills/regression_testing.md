# Regression Testing Skill

## 說明...
回歸測試旨在確保新更改不會破壞現有功能。視覺回歸測試則專注於檢測 UI 變化。此技能包括設置測試環境、撰寫測試腳本以及生成和比較視覺快照。

## 關鍵代碼片段或模式
```javascript
// Example of a visual regression test with Playwright
await expect(page).toHaveScreenshot('baseline.png', { threshold: 0.2 });
```

## 常見錯誤及避免方法
- **錯誤**：快照測試失敗，因為快照圖片與基準圖片之間的差異過大。
  **解決方法**：調整閾值參數以允許合理的視覺變化，或手動更新基準快照。