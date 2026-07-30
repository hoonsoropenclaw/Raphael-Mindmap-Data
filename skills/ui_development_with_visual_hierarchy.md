# UI Development with Visual Hierarchy

## 說明...
此微技能涉及使用視覺層級原則來設計和開發用戶界面，包括顏色、字體、佈局和組件的層級結構。

## 關鍵代碼片段或模式
```css
/* 定義顏色主題 */
:root {
  --bg-0: #0a0e1a;
  --bg-1: #111827;
  --bg-2: #1a2233;
  --text-1: #e6edf7;
  --text-2: #9aa8c0;
  --accent: #7aa9ff;
  /* 其他變量 */
}

/* 應用視覺層級 */
header {
  background: var(--bg-1);
  color: var(--text-1);
  /* 其他樣式 */
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  /* 其他樣式 */
}
```

## 常見錯誤及避免方法
- **顏色衝突**：使用 CSS 變量來統一管理顏色，避免顏色衝突和不一致。
- **層級不清晰**：通過調整組件的佈局和樣式來確保視覺層級清晰，例如使用不同的背景色、邊框和陰影來區分層級。