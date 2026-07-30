# 獨立網頁應用程式開發 (standalone_web_application_development)

## 概述
本技能涵蓋使用 React 和 Babel 構建完全獨立的網頁應用程式，無需依賴外部工具鏈或伺服器資源。應用程式將被打包成單一的 HTML 文件，包含所有必要的 JavaScript、CSS 和模擬持久化（如 localStorage），並在瀏覽器中直接運行。

## 主要技術與工具
- **React**：用於構建用戶界面。
- **Babel Standalone**：在瀏覽器中即時編譯 React JSX 程式碼。
- **HTML/CSS/JavaScript**：構建應用程式的核心技術。
- **localStorage**：模擬持久化數據存儲。

## 關鍵實現步驟

### 1. 設置單一 HTML 文件應用

將所有必要的資源內嵌到單一的 HTML 文件中，確保應用程式完全自包含。

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>獨立網頁應用程式</title>
  <style>
    /* 內嵌 CSS 樣式 */
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 0;
      background-color: #f0f0f0;
    }
    /* 其他樣式 */
  </style>
</head>
<body>
  <div id="root"></div>

  <!-- React 18 + Babel Standalone -->
  <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

  <!-- 應用程式 JSX 代碼 -->
  <script type="text/babel">
    const { useState, useEffect } = React;

    const App = () => {
      const [count, setCount] = useState(() => {
        // 使用 localStorage 模擬持久化
        const storedCount = localStorage.getItem('count');
        return storedCount ? parseInt(storedCount, 10) : 0;
      });

      useEffect(() => {
        localStorage.setItem('count', count);
      }, [count]);

      return (
        <div style={{ textAlign: 'center', marginTop: '50px' }}>
          <h1>計數器</h1>
          <p>當前計數: {count}</p>
          <button onClick={() => setCount(count + 1)}>增加</button>
          <button onClick={() => setCount(count - 1)}>減少</button>
        </div>
      );
    };

    ReactDOM.render(<App />, document.getElementById('root'));
  </script>
</body>
</html>
```

### 2. 使用 Babel Standalone 編譯 React JSX

在瀏覽器中引入 Babel Standalone 以編譯 JSX 程式碼：

```html
<!-- React 18 + Babel Standalone -->
<script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
```

### 3. 處理常見錯誤與性能優化

#### 錯誤：React 程式碼未正確編譯
- **解決方法**：確保 Babel 腳本正確引入，並將 `<script>` 標籤的 `type` 屬性設置為 `text/babel`。

#### 錯誤：性能問題
- **解決方法**：僅在開發環境中使用 Babel Standalone。對於生產環境，建議使用預編譯的程式碼，例如通過構建工具（如 Webpack 或 Parcel）進行打包。

### 4. 模擬持久化存儲

使用 `localStorage` 來模擬數據持久化：

```javascript
const localStorage = {
  _s: {},
  getItem(k) { return this._s[k] || null; },
  setItem(k, v) { this._s[k] = String(v); },
  removeItem(k) { delete this._s[k]; }
};

// 使用範例
localStorage.setItem('key', 'value');
const value = localStorage.getItem('key');
```

### 5. 跨瀏覽器兼容性

在開發過程中進行跨瀏覽器測試，並使用 polyfills 或降級方案處理不兼容問題。例如，使用 Babel 來轉譯現代 JavaScript 語法，使其在舊版瀏覽器中運行。

## 總結

通過將 React 和 Babel Standalone 結合使用，可以快速構建獨立的網頁應用程式，無需複雜的構建工具鏈。內嵌所有資源和模擬持久化存儲，確保應用程式在離線環境下也能正常運行。同時，注意性能優化和跨瀏覽器兼容性，以提供更好的用戶體驗。