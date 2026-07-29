# Babel Runtime Classic Configuration

## 說明...
在 UMD 環境中，React 的 automatic runtime 會嘗試導入 `react/jsx-runtime`，這在沒有模組解析器的情況下會導致錯誤。通過將 Babel preset 配置為使用經典運行 模式，可以避免這個問題。

## 關鍵代碼片段或模式
```javascript
const compiled = Babel.transform(src, {
  presets: [['react', { runtime: 'classic' }]],
  filename: 'app-inline'
}).code;
```