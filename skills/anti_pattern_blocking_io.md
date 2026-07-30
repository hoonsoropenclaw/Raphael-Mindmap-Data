# Anti-Pattern: Blocking I/O

## 說明...

### 原因
在主線程中執行阻塞的 I/O 操作，導致應用無響應。

### 關鍵代碼片段
```javascript
// 示例：阻塞 I/O 操作
function blockingIO() {
  const fs = require('fs');
  const data = fs.readFileSync('/path/to/file');
  return data;
}
```

### 解決方法
- **使用異步 I/O**：使用異步函數或 Promise 來執行 I/O 操作。
- **使用異步庫**：使用如 async.js 或 RxJS 這樣的異步庫來管理 I/O 操作。
- **分離主線程**：將阻塞操作移到工作線程或子進程中。