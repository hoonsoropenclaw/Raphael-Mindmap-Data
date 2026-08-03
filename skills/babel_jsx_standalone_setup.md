# Babel Standalone JSX Setup

## 說明...
Babel Standalone 允許在瀏覽器中直接轉譯 JSX 代碼。此技能包含如何正確設置 Babel Standalone 以轉譯 JSX，並避免常見的配置錯誤。

## 關鍵代碼片段或模式
```html
<!-- 引入 Babel Standalone -->
<script src="https://unpkg.com/@babel/standalone@7.25.7/babel.min.js"></script>

<!-- Babel 轉譯標籤 -->
<script type="text/babel" data-type="module">
  // JSX 代碼
</script>
```

## 常見錯誤及避免方法
- **錯誤**：同時設置 `data-presets="react"` 和 `data-type="module"`，導致 Babel 忽略 presets。
  **解決方法**：如果使用 `data-type="module"`，則不需要設置 `data-presets="react"`，因為 Babel 會自動處理模塊中的 JSX。
- **錯誤**：未正確設置 Babel 轉譯標籤的 `type` 屬性，導致 JSX 代碼未被轉譯。
  **解決方法**：確保 `type` 屬性設置為 `text/babel` 或 `text/jsx`，並且包含 Babel Standalone 庫。