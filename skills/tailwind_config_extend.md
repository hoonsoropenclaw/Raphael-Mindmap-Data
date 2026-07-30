# Tailwind Config Extend

## 說明
此微技能涉及擴展 Tailwind CSS 的配置文件，以添加自定義顏色、字體和陰影等，從而滿足特定設計需求。

## 關鍵代碼片段
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        ink: '#071b22',
        lagoon: '#127b78',
        mint: '#6ed3bd',
        ice: '#dff8f2',
        coral: '#ff8c78',
      },
      fontFamily: {
        sans: ['"Noto Sans TC"', '"PingFang TC"', 'sans-serif'],
        display: ['"Avenir Next"', '"Noto Sans TC"', 'sans-serif'],
      },
      boxShadow: {
        glass: '0 20px 60px rgba(0,24,32,.25)',
        inset: 'inset 0 1px 0 rgba(255,255,255,.28)',
      },
    },
  },
}
```

## 常見錯誤及避免方法
- **錯誤**：擴展配置時出現語法錯誤，導致 Tailwind 編譯失敗。
  **解決方法**：使用編輯器的語法檢查功能，並在修改配置後運行 `npx tailwindcss -i input.css -o output.css --watch` 以即時捕捉錯誤。
- **錯誤**：忘記在 HTML 中引入修改後的 CSS 文件。
  **解決方法**：確保在 HTML 文件的 `<head>` 部分正確引入編譯後的 CSS 文件，例如 `<link href="dist/output.css" rel="stylesheet">`。