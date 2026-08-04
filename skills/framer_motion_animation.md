# Framer Motion Animation

## 說明...
Framer Motion 提供了 `animate` 函式式 API，可以對 DOM 元素進行動畫控制，支持多種動畫類型，如 spring、keyframes 等。

## 關鍵程式碼片段
```javascript
const anim = animate(card, {
  y: [30, -20, 10, -5, 0],
  rotate: [0, 5, -3, 1, 0],
  scale: [0.8, 1.05, 0.97, 1.02, 1],
}, { duration: 1.1, ease: 'easeInOut' });
```

## 常見錯誤及避免方法
- **錯誤**: 動畫參數設置錯誤，導致動畫效果不如預期。
  **解決方法**: 仔細檢查動畫參數，確保數值和動畫類型正確。
- **錯誤**: 動畫未觸發，可能是選擇器錯誤或元素未加載。
  **解決方法**: 確認選擇器正確，並在動畫前確保元素已加載。