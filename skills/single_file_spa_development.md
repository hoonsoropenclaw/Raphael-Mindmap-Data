# Single File SPA Development

## 說明...

### 目的
開發一個單頁應用（SPA），將所有資源打包到一個 HTML 文件中，實現快速部署和簡化部署流程。

### 關鍵代碼片段
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Single File SPA</title>
  <script src="https://esm.sh/react@18.3.1" type="module"></script>
  <!-- 其他依賴項 -->
</head>
<body>
  <div id="root"></div>
  <script type="module">
    import React from 'https://esm.sh/react@18.3.1';
    import ReactDOM from 'https://esm.sh/react-dom@18.3.1';
    
    function App() {
      return <h1>Hello, Single File SPA!</h1>;
    }
    
    ReactDOM.createRoot(document.getElementById('root')).render(<App />);
  </script>
</body>
</html>
```

### 常見錯誤及避免方法
- **錯誤**：ESM 模塊加載失敗。
  **解決方法**：使用 importmap 來管理模塊依賴，並確保服務器支持 ESM。
- **錯誤**：瀏覽器兼容性問題。
  **解決方法**：在開發過程中檢查目標瀏覽器的兼容性，並使用 polyfills 來解決兼容問題。