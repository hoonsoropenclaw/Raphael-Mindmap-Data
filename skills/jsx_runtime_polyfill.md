# JSX Runtime Polyfill

## 說明...

### 目的
在瀏覽器中實現 JSX 運行時 polyfill，以便在不使用 Babel 編譯的情況下使用 JSX 語法。

### 關鍵代碼片段
```html
<script src="https://cdn.jsdelivr.net/npm/react@18.3.1/umd/react.production.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/react-dom@18.3.1/umd/react-dom.production.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/react-jsx-runtime@18.3.1/umd/react-jsx-runtime.production.min.js"></script>

<script type="module">
  import { jsx as _jsx } from 'https://esm.sh/react@18.3.1/jsx-runtime';
  // 其他 JSX 代碼
</script>
```

### 常見錯誤及避免方法
- **錯誤**：JSX 語法無法被正確解析。
  **解決方法**：確保 JSX 運行時 polyfill 已正確加載，並使用 ESM 模塊來管理依賴。
- **錯誤**：React 和 React DOM 版本不兼容。
  **解決方法**：使用與 JSX 運行時 polyfill 兼容的 React 和 React DOM 版本。