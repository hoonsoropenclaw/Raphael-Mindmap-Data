# Glassmorphism Design

## 說明...
應用 Glassmorphism 設計風格，通過設置背景透明度、模糊效果和陰影來實現具有景深感的 UI 元素。

## 關鍵程式碼片段或模式...
```css
.glass {
  background: var(--glass);
  border: 1px solid var(--line);
  box-shadow: 0 24px 80px rgba(0, 10, 28, .28);
  -webkit-backdrop-filter: blur(22px) saturate(135%);
  backdrop-filter: blur(22px) saturate(135%);
}
```

## 常見錯誤及避免方法...
- **錯誤**：模糊效果導致文字難以閱讀。
  **解決方法**：調整 `--glass` 和 `--line` 的顏色和透明度，或在模糊背景上添加文字陰影以提高可讀性。
- **錯誤**：在不支持 `backdrop-filter` 的瀏覽器中，玻璃效果無法顯示。
  **解決方法**：使用 `@supports` 查詢來提供回退樣式，例如使用純色背景代替玻璃效果。