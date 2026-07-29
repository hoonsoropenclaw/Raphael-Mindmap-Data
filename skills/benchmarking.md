# Benchmarking

## 說明
進行基準測試以比較不同方案的性能，例如 REST 與 GraphQL 的比較。

## 關鍵代碼片段
```javascript
const samples = {
  restFanOut: [],
  restBatched: [],
  graphqlCold: [],
  graphqlWarm: [],
};
```

## 常見錯誤及避免方法
- **錯誤**：基準測試方法不當或結果不可靠。
  - **解決方法**：確保測試環境一致，使用多輪測試取中位數，並排除外部干擾。