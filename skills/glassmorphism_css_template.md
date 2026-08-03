# Glassmorphism CSS Template

## 說明
此微技能提供了一個可重用的 Glassmorphism 樣式模板，基於 Tailwind CSS 實現，包含動態主題切換、模糊效果和透明度控制。

## 關鍵代碼片段
```html
<div class="glassmorphism bg-white/30 backdrop-blur-md rounded-lg p-6">
  <!-- 內容 -->
</div>
```

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer utilities {
  .glassmorphism {
    @apply bg-white/30 backdrop-blur-md;
  }
}
```

## 常見錯誤及解決方法
1. **瀏覽器兼容性問題**：部分瀏覽器可能不支持 `backdrop-filter` 屬性。解決方法：在 CSS 中添加 `@supports not (backdrop-filter: blur(1px))` 回退樣式。
2. **性能問題**：過度使用模糊效果可能導致頁面性能下降。建議僅在必要的元素上使用，並控制模糊半徑。