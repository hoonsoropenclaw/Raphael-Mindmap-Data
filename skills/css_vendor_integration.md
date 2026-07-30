# CSS Vendor Integration

## 說明...
將第三方庫的 CSS 樣式表本地化，並在項目中正確引入，以避免依賴外部 CDN。

## 關鍵代碼片段或模式
```html
<!-- 本地引入 React Flow CSS -->
<link rel="stylesheet" href="vendor/reactflow.css" />

<!-- 主樣式表 -->
<link rel="stylesheet" href="css/main.css" />
```

## 常見錯誤及避免方法
- **錯誤**: 樣式表路徑錯誤，導致 CSS 無法正確加載。
  **解決方法**: 確認 `href` 屬性中的路徑與實際文件位置匹配。
- **錯誤**: 缺少對 CSS 變量的定義，導致樣式無法正常應用。
  **解決方法**: 在主樣式表中定義所有必要的 CSS 變量，或確保引入的 CSS 文件中已包含這些定義。