# Will-Change Management

## 說明...
`will-change` 屬性可以提前通知瀏覽器元素將要進行動畫，從而優化性能。但若不當使用，可能導致內存問題。

## 關鍵程式碼片段
```javascript
// 動畫開始時設置 will-change
el.style.willChange = 'transform, opacity, filter';
// 動畫結束後卸載 will-change
anim.then(() => { el.style.willChange = 'auto'; });
```

## 常見錯誤及避免方法
- **錯誤**: 永久設置 `will-change`，導致內存膨脹。
  **解決方法**: 僅在動畫期間設置 `will-change`，動畫結束後及時卸載。
- **錯誤**: 設置過多的 `will-change` 屬性，導致性能問題。
  **解決方法**: 僅設置必要的屬性，避免過度優化。