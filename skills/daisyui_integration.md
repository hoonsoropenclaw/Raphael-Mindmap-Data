# DaisyUI 與 Tailwind CSS 的集成

## 說明...
DaisyUI 是一個基於 Tailwind CSS 的主題和組件庫。在這個例子中，我們集成了 DaisyUI 並配置了六個主題（light, dark, corporate, business, emerald, autumn）。

## 關鍵代碼片段
```css
/* globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn {
    @apply ...;
  }
  /* 其他 DaisyUI 組件樣式 */
}

/* 設置主題 */
[data-theme="light"] {
  --color-primary: ...;
  /* 其他主題變量 */
}
```

## 常見錯誤及避免方法
- **錯誤**: DaisyUI 類名與 Tailwind 類名衝突，導致樣式問題。
  **避免方法**: 確保 DaisyUI 和 Tailwind 的配置正確，並檢查類名衝突。
- **錯誤**: 主題切換不起作用。
  **避免方法**: 確認 `ThemeProvider` 正確包裹應用，並檢查 `localStorage` 中的主題設置。