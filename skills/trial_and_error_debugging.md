# Trial and Error Debugging

## 說明...

### 目的
在缺乏明確錯誤信息或文檔的情況下，通過不斷嘗試和調整來解決問題。

### 關鍵代碼片段
```javascript
// 示例：嘗試不同的 API 調用方式
function fetchData() {
  try {
    // 第一種嘗試
    return fetch('/api/data').then(res => res.json());
  } catch (e) {
    // 第二種嘗試
    return fetch('/api/data').then(res => res.text()).then(text => JSON.parse(text));
  }
}
```

### 常見錯誤及避免方法
- **錯誤**：過度依賴試錯，導致效率低下。
  **解決方法**：在開始試錯前，盡量收集更多信息，例如錯誤日誌或用戶反饋。
- **錯誤**：忽略潛在的副作用，導致新問題出現。
  **解決方法**：在每次嘗試後，仔細檢查應用的狀態和行為。