# Browser Console Debugging

## 說明...
此技能涉及使用瀏覽器控制台來捕獲和調試 JavaScript 錯誤，包括全局錯誤處理和日誌記錄。

## 關鍵代碼片段或模式
```html
<script>
window.addEventListener('error', e => {
  document.getElementById('log').textContent += `[ERROR] ${e.message}\n  at ${e.filename}:${e.lineno}\n  ${e.error?.stack || ''}\n\n`;
});
window.addEventListener('unhandledrejection', e => {
  document.getElementById('log').textContent += `[REJECT] ${e.reason}\n  ${e.reason?.stack || ''}\n\n`;
});
const origLog = console.log;
console.log = (...a) => {
  document.getElementById('log').textContent += `[LOG] ${a.map(x=>String(x)).join(' ')}\n`;
  origLog(...a);
};
console.error = (...a) => {
  document.getElementById('log').textContent += `[ERR] ${a.map(x=>String(x)).join(' ')}\n`;
};
</script>
```

## 常見錯誤及避免方法
- **錯誤**：全局錯誤處理器未正確設置，導致錯誤未被捕獲。
  **解決方法**：確保 `window.addEventListener('error', ...)` 和 `window.addEventListener('unhandledrejection', ...)` 正確設置。
- **錯誤**：日誌記錄函式未正確覆蓋，導致日誌無法顯示。
  **解決方法**：檢查 `console.log` 和 `console.error` 是否正確覆蓋，並確保日誌元素存在於 DOM 中。