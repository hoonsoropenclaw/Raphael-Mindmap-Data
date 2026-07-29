# Importmap Configuration

## 說明...
### 目的
使用 importmap 來管理應用中的模組依賴，特別是在瀏覽器環境中。

### 關鍵代碼片段
```html
<script type="importmap">
{
  "imports": {
    "react": "https://esm.sh/react@18.3.1",
    "react-dom/client": "https://esm.sh/react-dom@18.3.1/client?deps=react@18.3.1",
    "reactflow": "https://esm.sh/reactflow@11.11.4?deps=react@18.3.1,react-dom@18.3.1&external=react,react-dom"
  }
}
</script>
```

### 常見錯誤及避免方法
- **錯誤**：模組無法正確加載。
  **解決方法**：確保 importmap 中的 URL 是正確的，並且目標模組支持 ESM。
- **錯誤**：循環依賴導致錯誤。
  **解決方法**：檢查模組之間的依賴關係，避免循環依賴。
- **錯誤**：瀏覽器不支持 importmap。
  **解決方法**：使用 polyfill 或轉換工具來支持舊版瀏覽器。