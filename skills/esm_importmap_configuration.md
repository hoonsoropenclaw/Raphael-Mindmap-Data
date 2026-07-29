# ESM Importmap Configuration

## 說明...

### 目的
通過 ESM 和 importmap 動態載入 React、ReactDOM 和其他庫，實現無需構建步驟的開發流程。

### 關鍵代碼片段
```html
<script type="importmap">
  {
    "imports": {
      "react": "https://esm.sh/react@18.3.1",
      "react-dom": "https://esm.sh/react-dom@18.3.1",
      "react/jsx-runtime": "https://esm.sh/react@18.3.1/jsx-runtime",
      "@xyflow/react": "https://esm.sh/@xyflow/react@12.3.5?bundle&deps=react@18.3.1,react-dom@18.3.1",
      "@xyflow/react/dist/style.css": "https://esm.sh/@xyflow/react@12.3.5/dist/style.css"
    }
  }
</script>
```

### 常見錯誤及避免方法
- **錯誤**：importmap 不支持子路徑，導致 CSS 導入失敗。
- **避免方法**：將 CSS 樣式表作為單獨的 `<link>` 標籤引入，而不是通過 importmap 導入。