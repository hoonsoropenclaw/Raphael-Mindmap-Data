# ESM.sh Bundling and Importmap Configuration

## 說明...
此技能涉及使用 esm.sh 提供的 CDN 服務來打包和提供 JavaScript 模塊，並通過 importmap 配置模塊的導入路徑。

## 關鍵代碼片段或模式
```html
<script type="importmap">
{
  "imports": {
    "react": "https://esm.sh/react@18.3.1",
    "react-dom": "https://esm.sh/react-dom@18.3.1",
    "react-dom/client": "https://esm.sh/react-dom@18.3.1/client",
    "react/jsx-runtime": "https://esm.sh/react@18.3.1/jsx-runtime",
    "@xyflow/react": "https://esm.sh/@xyflow/react@12.3.5?external=react,react-dom"
  }
}
</script>
```

## 常見錯誤及避免方法
- **錯誤**：importmap 無法解析 CSS 子路徑。
  **解決方法**：使用 `<link>` 標籤通過 esm.sh 的 CSS endpoint 引入 CSS，或將 CSS 直接內聯到 HTML 中。
- **錯誤**：依賴模塊未正確列出在 importmap 中，導致模塊無法導入。
  **解決方法**：確保所有依賴模塊都正確列在 importmap 中，並使用正確的版本號和路徑。