# Tailwind CSS Integration

## 說明...
Tailwind CSS 是一個實用程序優先的 CSS 框架。此技能涵蓋如何將 Tailwind CSS 引入 React 應用中，包括使用 CDN 或構建工具（如 Webpack）進行整合，以及使用 Tailwind 的類來設計組件。

## 關鍵代碼片段或模式
```html
<!-- 使用 CDN 引入 Tailwind CSS -->
<script src="https://cdn.tailwindcss.com"></script>
<script>
  tailwind.config = {
    darkMode: 'class',
    theme: {
      extend: {
        colors: {
          ink: { /* ... */ },
          accent: { /* ... */ },
          // 更多顏色
        },
        keyframes: { /* ... */ },
        animation: { /* ... */ },
      },
    },
  };
</script>
```

## 常見錯誤及避免方法
- **類名拼寫錯誤**：Tailwind 的類名是大小寫敏感的，確保正確拼寫。
- **未使用自定義配置**：如果需要自定義顏色或主題，確保在 `tailwind.config.js` 中正確配置並在 HTML 中引入。
- **CSS 衝突**：Tailwind 的類名可能與其他 CSS 框架或自定義樣式衝突，考慮使用 CSS Modules 或其他命名空間策略來避免衝突。