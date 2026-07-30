# Glassmorphism Design System

## 說明
此技能涉及在網頁中實現玻璃態（Glassmorphism）設計，包括使用背景模糊和半透明背景來創造深度和層次感。

## 關鍵代碼片段
```css
.glass {
    background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.025));
    border: 1px solid rgba(255,255,255,.10);
    backdrop-filter: blur(14px) saturate(140%);
    -webkit-backdrop-filter: blur(14px) saturate(140%);
    box-shadow: 0 12px 40px -10px rgba(0,0,0,.55), inset 0 1px 0 rgba(255,255,255,.06);
}
```

## 常見錯誤及避免方法
- **錯誤**：背景模糊效果導致文本可讀性差。
  **解決方法**：調整 `backdrop-filter` 的模糊程度和背景透明度，確保文本清晰可讀。
- **錯誤**：玻璃態元素在某些瀏覽器中無法正確渲染。
  **解決方法**：使用供應商前綴（如 `-webkit-`）並提供回退樣式以提高兼容性。