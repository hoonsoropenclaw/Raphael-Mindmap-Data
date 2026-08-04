# Anti-Pattern: Blocking I/O

## 說明...
阻塞性 I/O 操作會導致主線程被阻塞，從而影響應用程序的響應性。

## 關鍵程式碼片段
```javascript
// 錯誤示例: 阻塞性 I/O 操作
const data = fs.readFileSync('/path/to/file');
```

## 常見錯誤及避免方法
- **錯誤**: 使用同步的 I/O 操作，導致主線程阻塞。
  **解決方法**: 使用異步的 I/O 操作，如 `fs.readFile` 或 `fs.promises.readFile`，並使用 `await` 來處理異步結果。
- **錯誤**: 長時間運行的 I/O 操作未使用超時機制。
  **解決方法**: 設置合理的超時時間，並在超時時進行相應處理。