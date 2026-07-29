# Dynamic Visual Hierarchy

## 說明...
此微技能涵蓋如何通過 CSS 和 JavaScript 實現動態視覺層級和微動畫，例如節點的懸停效果、狀態變化動畫，以及邊線的流動動畫。

## 關鍵程式碼片段或模式
```css
.node-card:hover {
  transform: translateY(-5px) rotate(-.4deg);
  box-shadow: 12px 16px 0 rgba(18,32,43,.13);
  border-color: var(--ink);
}

.edge-flow {
  stroke-dasharray: 6 8;
  animation: flow 1.6s linear infinite;
}

@keyframes flow {
  to {
    stroke-dashoffset: -28;
  }
}
```

## 常見錯誤及避免方法
- **錯誤**：動畫未觸發。
  **解決方法**：檢查 CSS 動畫關鍵幀是否正確設置，並確認動畫類別已正確應用到目標元素上。
- **錯誤**：動畫卡頓或不流暢。
  **解決方法**：優化動畫的複雜度，減少重排和重繪的頻率，並使用硬件加速的 CSS 屬性。