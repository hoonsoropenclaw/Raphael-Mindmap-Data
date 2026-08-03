# Path Resolution Fix

## 說明...
此技能用於解決 HTML 文件中資源路徑解析錯誤的問題，確保在不同的打開方式下資源都能正確加載。

## 關鍵代碼片段或模式
```javascript
function buildGallery(cases, pathBase) {
  const gallery = [];
  for (const c of cases) {
    if (!c.paths || !c.paths.current || !fs.existsSync(c.paths.current)) continue;
    ...
    <img src="${pathBase}screenshots/${esc(shotName)}" alt="${esc(c.browser)} ${esc(c.page)}" loading="lazy"
          style="width:100%;display:block;background:#fafbfc;" />
    ...
  }
  return gallery.join('') || '<p style="color:#656d76;font-size:13px;">No screenshots available.</p>';
}
```

## 常見錯誤及避免方法
- **錯誤**：相對路徑錯誤，導致資源無法加載。
  **解決方法**：根據 HTML 文件的位置動態計算路徑，例如使用 `pathBase` 參數來設置基礎路徑。
- **錯誤**：重複代碼，導致維護困難。
  **解決方法**：使用函數封裝路徑解析邏輯，避免在多個地方重複代碼。