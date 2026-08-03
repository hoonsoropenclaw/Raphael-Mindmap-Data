# Progressive Reveal Animation

## 說明...
使用 CSS keyframes 和自定義變量來實現元素漸進式顯示的動畫效果。

## 關鍵程式碼片段或模式...
```css
.reveal {
  animation: reveal .65s both;
  animation-delay: var(--delay, 0ms);
}
@keyframes reveal {
  from {
    opacity: 0;
    transform: translateY(18px) scale(.985);
  }
  to {
    opacity: 1;
    transform: none;
  }
}
```

## 常見錯誤及避免方法...
- **錯誤**：動畫延遲時間設置過長或過短，導致效果不自然。
  **解決方法**：根據設計需求調整 `--delay` 變量的值，並在多個設備上測試動畫效果。
- **錯誤**：動畫屬性衝突，導致動畫無法正常播放。
  **解決方法**：檢查 CSS 中是否有其他樣式或腳本干擾動畫屬性，並確保動畫屬性優先級正確。