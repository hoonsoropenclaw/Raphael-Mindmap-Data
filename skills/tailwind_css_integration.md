# Tailwind CSS Integration

## 說明...
此微技能涵蓋如何將 Tailwind CSS 整合到 React 應用中，包括引入 CDN、使用 Tailwind 類別進行樣式設計，以及自定義主題。

## 關鍵程式碼片段或模式
```html
<head>
  <link href="https://cdn.tailwindcss.com" rel="stylesheet">
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            'ink': '#12202b',
            'paper': '#edf2ed',
            // 其他自定義顏色
          }
        }
      }
    };
  </script>
</head>
```

## 常見錯誤及避免方法
- **錯誤**：Tailwind 類別未生效。
  **解決方法**：確保已正確引入 Tailwind CSS 的 CDN 或本地資源，並檢查是否有其他 CSS 框架衝突。
- **錯誤**：自定義主題未生效。
  **解決方法**：確認 tailwind.config.js 或內聯配置中的主題設置正確，並重新編譯或刷新頁面。