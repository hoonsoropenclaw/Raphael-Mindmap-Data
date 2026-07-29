# HTML UI Layout Design

## 說明...
此微技能涉及使用 HTML 和 CSS 構建具有視覺吸引力的用戶界面，包括布局設計、色彩搭配和響應式設計。

## 關鍵程式碼片段或模式
```html
<div class="container">
  <header>
    <h1>智能日程安排助手</h1>
    <p>輕鬆管理您的日程安排</p>
  </header>
  <div class="layout">
    <aside>
      <!-- 左側導航或過濾器 -->
    </aside>
    <main>
      <!-- 主內容區域 -->
    </main>
  </div>
</div>
```

```css
.container {
  max-width: 1400px;
  margin: 0 auto;
}
.layout {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 24px;
}
```

## 常見錯誤及避免方法
- **布局不靈活**：使用 CSS Grid 或 Flexbox 來實現靈活的布局，避免使用過時的表格布局。
- **響應式設計問題**：使用相對單位（如百分比、em、rem）和媒體查詢來確保界面在不同設備上都能良好顯示。
- **色彩搭配不協調**：使用 CSS 變量來統一色彩主題，並參考設計系統（如 Tailwind CSS 或 Material Design）來選擇合適的色彩。