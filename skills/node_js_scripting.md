# Node.js Scripting

## 說明
Node.js 是一個強大的 JavaScript 運行時環境，可用於編寫腳本以自動化各種任務。此技能涵蓋如何使用 Node.js 編寫腳本來操作文件、執行系統命令和處理數據。

## 關鍵代碼片段
```javascript
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'web_output.html');
fs.readFile(filePath, 'utf8', (err, data) => {
  if (err) {
    console.error('Error reading file:', err);
    return;
  }
  // 處理數據
  console.log('File contents:', data);
});
```

## 常見錯誤及避免方法
1. **文件路徑錯誤**：使用 `path` 模塊來處理文件路徑，避免因路徑錯誤導致的文件操作失敗。
2. **權限問題**：確保腳本有足夠的權限來執行所需的文件操作。
3. **異步操作處理不當**：使用異步函數或 `Promise` 來處理文件操作，避免阻塞事件循環。
