# Bar Chart with ScaleY Animation

## 說明...
使用 Framer Motion 的 scaleY 動畫來實現柱狀圖的進場效果，並通過 transform-origin 屬性確保動畫從底部開始。

## 關鍵程式碼片段或模式
```jsx
<motion.div
  initial={{ scaleY: 0, opacity: 0 }}
  animate={{ scaleY: value, opacity: 1 }}
  transition={{ duration: 0.9, ease: [0.2, 0.8, 0.2, 1] }}
  style={{ transformOrigin: 'bottom', height: '100%' }}
  className="w-full rounded-xl bar-fill shadow-glow relative group cursor-pointer"
>
  <!-- 內容 -->
</motion.div>
```

## 常見錯誤及避免方法
- **錯誤**：柱狀圖高度無法正確顯示。
  **解決方法**：確保父容器有明確的高度，並使用 `transform-origin: bottom` 來控制動畫的起始點。
- **錯誤**：動畫不流暢。
  **解決方法**：調整動畫的持續時間和緩動函數，例如使用 `ease` 或 `ease-in-out`。