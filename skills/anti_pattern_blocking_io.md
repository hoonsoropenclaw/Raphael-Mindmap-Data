# Anti-Pattern: Blocking I/O

## 說明...
此技能描述了由於阻塞 I/O 操作導致的程序掛起問題，並提供了解決方法。

## 關鍵代碼片段或模式
```javascript
// 錯誤示例：使用同步文件操作導致阻塞
const data = fs.readFileSync('/path/to/file');

// 正確示例：使用異步文件操作
fs.readFile('/path/to/file', (err, data) => {
  if (err) throw err;
  console.log(data);
});
```

## 常見錯誤及避免方法
- **錯誤**：在主線程中執行阻塞 I/O 操作，導致程序掛起。
  **解決方法**：使用異步 I/O 操作，例如使用 `fs.readFile` 而不是 `fs.readFileSync`。
- **錯誤**：在事件循環中執行長時間運行的任務。
  **解決方法**：將長時間運行的任務移到工作線程或使用異步模式。