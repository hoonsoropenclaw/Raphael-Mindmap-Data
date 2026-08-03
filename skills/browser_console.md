# Browser Console

## 說明
此技能用於在瀏覽器控制台中執行指定的JavaScript代碼，並獲取執行結果。

## 關鍵代碼片段
```python
result = page.evaluate('1 + 2')
```

## 常見錯誤及避免方法
- **錯誤**：JavaScript代碼語法錯誤。
  **解決方法**：在執行前檢查JavaScript代碼的語法。

- **錯誤**：執行結果無法序列化。
  **解決方法**：確保執行結果可以序列化為JSON。