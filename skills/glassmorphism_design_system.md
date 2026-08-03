# Glassmorphism Design System

## 說明...
### 目的
實現 Glassmorphism 設計風格，包括玻璃化效果、動態主題切換和無障礙支持。

### 關鍵程式碼片段或模式
```html
<!-- 玻璃化效果的範例 -->
<div class="glass-soft backdrop-blur-xl bg-white/30">
  <!-- 內容 -->
</div>
```

### 常見錯誤及避免方法
- **錯誤**：玻璃化效果在舊瀏覽器中無法顯示。
  **解決方法**：使用 `@supports` 檢查 `backdrop-filter` 的支持情況，並提供備用樣式。
- **錯誤**：動態主題切換未正確實現。
  **解決方法**：使用 JavaScript 來監聽主題切換事件，並更新相應的 `data-theme` 屬性。
