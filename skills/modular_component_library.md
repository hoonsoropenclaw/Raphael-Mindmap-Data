# Modular Component Library

## 說明...
此微技能旨在構建一個模組化的 UI 組件庫，將不同類型的組件（如按鈕、卡片、輸入框等）進行分類和組織，以便於重用和維護。

## 關鍵程式碼片段或模式
```html
<!-- Buttons -->
<button class="btn btn-primary">Primary Button</button>

<!-- Cards -->
<div class="card">
  <h2 class="card-title">Card Title</h2>
  <p class="card-body">Card content goes here.</p>
</div>
```

## 常見錯誤及避免方法
- **錯誤**：組件之間的命名衝突，導致樣式覆蓋。
  **解決方法**：使用命名空間或 BEM 命名法來避免類名衝突。
- **錯誤**：組件之間的依賴關係複雜，難以維護。
  **解決方法**：保持組件的獨立性和單一職責原則，減少不必要的依賴。