# Local Storage Integration

## 說明...
localStorage 是一種在瀏覽器中存儲數據的方法，數據在瀏覽器關閉後仍然存在。此技能涵蓋如何將數據保存到 localStorage 以及如何從中讀取數據。

## 關鍵代碼片段或模式
```javascript
// 保存數據到 localStorage
function saveToLocalStorage(key, data) {
  localStorage.setItem(key, JSON.stringify(data));
}

// 從 localStorage 讀取數據
function getFromLocalStorage(key) {
  const data = localStorage.getItem(key);
  return data ? JSON.parse(data) : null;
}

// 使用 debounce 防止頻繁寫入
function debounce(func, delay) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), delay);
  };
}

const debouncedSave = debounce(saveToLocalStorage, 400);
```

## 常見錯誤及避免方法
- **數據未序列化**：localStorage 只能存儲字符串，確保在存儲前將對象序列化為 JSON。
- **未處理讀取錯誤**：在讀取數據時，檢查數據是否存在以及是否為有效的 JSON。
- **頻繁寫入導致性能問題**：使用 debounce 技術來限制寫入頻率，避免頻繁操作 localStorage 影響性能。