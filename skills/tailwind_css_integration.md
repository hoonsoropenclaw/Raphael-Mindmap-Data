# Tailwind CSS Integration

## 說明...
### 目的
將 Tailwind CSS 整合到前端專案中，並利用其主題擴展功能來自訂顏色、陰影和動畫。

### 關鍵程式碼片段或模式
```javascript
// Tailwind 主題擴展範例
tailwind.config = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      colors: {
        glass: {
          50:  'rgba(255,255,255,0.06)',
          100: 'rgba(255,255,255,0.10)',
          // 其他顏色
        },
        ink: { /* ... */ },
        brand: { /* ... */ },
        accent: { /* ... */ },
      },
      boxShadow: {
        'glass-sm': '0 4px 16px 0 rgba(2, 6, 23, 0.25)',
        'glass':    '0 8px 32px 0 rgba(2, 6, 23, 0.37)',
        // 其他陰影
      },
      animation: {
        'float-slow':  'float 14s ease-in-out infinite',
        // 其他動畫
      },
      keyframes: {
        float: {
          '0%,100%': { transform: 'translate(0px, 0px) scale(1)' },
          '50%':     { transform: 'translate(20px, -28px) scale(1.05)' },
        },
        // 其他 keyframes
      },
    },
  },
}
```

### 常見錯誤及避免方法
- **錯誤**：Tailwind 配置錯誤導致樣式未生效。
  **解決方法**：確保 `tailwind.config.js` 的語法正確，並在 HTML 中正確引入 Tailwind 的 CDN 或構建後的 CSS 文件。
- **錯誤**：自訂顏色或陰影未正確應用。
  **解決方法**：檢查 `extend` 部分中的鍵名是否正確，並確保在 HTML 中使用正確的類名。
