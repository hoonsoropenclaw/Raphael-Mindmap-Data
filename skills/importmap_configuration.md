# Importmap Configuration

## 說明...
此微技能涉及在 HTML 文件中使用 `<script type="importmap">` 標籤來配置 ESM 模組的引入路徑，從而實現無需構建工具的模組化開發。

## 關鍵代碼片段或模式
```html
<script type="importmap">
{
  "imports": {
    "react": "https://esm.sh/react@18.3.1",
    "react-dom": "https://esm.sh/react-dom@18.3.1",
    "framer-motion": "https://esm.sh/framer-motion@11.11.10?deps=react@18.3.1,react-dom@18.3.1&external=react,react-dom"
  }
}
</script>
```

## 常見錯誤及避免方法
- **錯誤**：importmap 中的鍵名拼寫錯誤或格式不正確，導致模組無法正確引入。
  **解決方法**：仔細檢查 importmap 中的鍵名，確保與代碼中使用的名稱完全一致。
- **錯誤**：CDN URL 無效或版本不匹配，導致模組無法加載。
  **解決方法**：驗證 CDN URL 的有效性，並確保版本號與項目需求相符。