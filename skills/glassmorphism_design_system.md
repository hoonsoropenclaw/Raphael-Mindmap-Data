# Glassmorphism Design System

## 說明
此微技能旨在使用 Tailwind CSS 實現 Glassmorphism 風格的設計系統，包括背景模糊、邊框、陰影和透明度等效果。

## 關鍵代碼片段
```css
.glass {
  background: rgba(14, 51, 60, 0.66);
  border: 1px solid rgba(194, 255, 241, 0.15);
  box-shadow: 0 20px 60px rgba(0, 24, 32, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.11);
  backdrop-filter: blur(18px) saturate(145%);
  -webkit-backdrop-filter: blur(18px) saturate(145%);
  border-radius: 18px;
}
```

## 常見錯誤及避免方法
- **錯誤**：過度使用 Glassmorphism 導致頁面視覺混亂。
  **解決方法**：限制 Glassmorphism 的使用範圍，僅在關鍵組件上應用，並確保整體設計的一致性。
- **錯誤**：忘記添加適當的 fallback 樣式，導致在不支持 backdrop-filter 的瀏覽器中顯示異常。
  **解決方法**：為關鍵組件提供簡單的 fallback 樣式，例如純色背景和標準邊框。