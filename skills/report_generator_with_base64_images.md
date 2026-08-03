# Report Generator with Base64 Images

## 說明...
此技能涉及將捕獲的截圖轉換為 base64 編碼，並將其嵌入到生成的 HTML 報告中。報告中包含 PASS/MINOR/FAIL 徽章、統計信息和報告元數據。

## 關鍵代碼片段或模式
```javascript
// 將 canvas 轉換為 base64 圖像
function canvasToBase64(canvas) {
  return canvas.toDataURL('image/png');
}

// 生成 HTML 報告
function generateReport(base64Images) {
  return `<!DOCTYPE html>
<html>
<head>
  <title>Visual Regression Report</title>
</head>
<body>
  <h1>Visual Regression Report</h1>
  <img src="${base64Images.baseline}" alt="Baseline"/>
  <img src="${base64Images.current}" alt="Current"/>
  <img src="${base64Images.diff}" alt="Diff"/>
  <p>Status: ${status}</p>
  <p>Pixel Difference: ${diffPixels}</p>
</body>
</html>`;
}
```

## 常見錯誤及錯誤避免方法
- **錯誤**: 生成的 HTML 報告中圖像未正確嵌入。
  **解決方法**: 確保 `canvas.toDataURL('image/png')` 返回的字符串正確嵌入到 `<img>` 標籤的 `src` 屬性中。
- **錯誤**: 報告中未包含足夠的元數據，導致難以理解報告內容。
  **解決方法**: 在報告中添加足夠的元數據，例如時間戳、版本信息等。