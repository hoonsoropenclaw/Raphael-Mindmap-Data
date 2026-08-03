# Advanced React Application with Design System

## 說明
構建一個基於 React Flow 的複雜應用，結合設計系統（如 Tailwind CSS）進行樣式管理。包含 z-index 管理、節點渲染、拖拽功能等。

## 關鍵程式碼片段
```javascript
// web_output.html
<div class="app-shell">
  <header class="topbar">
    <!-- Topbar content -->
  </header>
  <main class="canvas-wrap">
    <div id="flow"></div>
  </main>
  <footer class="status-bar">
    <!-- Status bar content -->
  </footer>
</div>
```

## 常見錯誤與解決方法
- **錯誤**：z-index 管理不當導致元素被遮擋。
  **解決方法**：明確設定每個元素的 z-index，並確保父元素的定位屬性正確。