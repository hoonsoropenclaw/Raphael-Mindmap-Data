# Theme Toggle Implementation

## 說明...
此技能涉及實現主題切換功能，使用戶能夠在淺色和深色模式之間切換。這通常涉及使用 CSS 變量來驅動顏色主題，並通過 JavaScript 來處理用戶交互和狀態管理。

## 關鍵代碼片段或模式
```html
<button id="theme-toggle">Toggle Theme</button>
```
```javascript
const toggleButton = document.getElementById('theme-toggle');
toggleButton.addEventListener('click', () => {
  document.documentElement.classList.toggle('dark-theme');
  // Save user preference to localStorage
  localStorage.setItem('theme', document.documentElement.classList.contains('dark-theme') ? 'dark' : 'light');
});
```

## 常見錯誤及避免方法
- **錯誤**：主題切換後，頁面元素未正確更新。
  **避免方法**：確保所有主題相關的 CSS 變量都正確應用，並在切換主題時重新渲染必要的元素。
- **錯誤**：主題切換狀態未持久化，導致用戶偏好丟失。
  **避免方法**：將用戶的主題偏好保存到 `localStorage` 或其他持久化存儲中，並在頁面加載時應用。