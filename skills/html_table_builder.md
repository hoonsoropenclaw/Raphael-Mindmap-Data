# HTML Table Builder

## 說明...
此技能用於根據數據生成 HTML 表格，並動態填充表格內容，例如狀態標籤、鏈接和格式化數據。

## 關鍵代碼片段或模式
```javascript
function functionalRow(c) {
  const isFail = c.status !== 'pass';
  return `<tr style="border-bottom:1px solid #eaeef2;${isFail ? 'background:#fff8f8;' : ''}">
    <td style="${cell()};font-family:ui-monospace,monospace;font-size:12px;">${esc(c.browser)}</td>
    <td style="${cell()};font-family:ui-monospace,monospace;font-size:12px;">${esc(c.name)}</td>
    <td style="${cell()};">${statusChip(c.status, FUNCTIONAL_STATUS)}</td>
    <td style="${cell()};font-size:12px;">${fmtMs(c.durationMs)}</td>
    <td style="${cell()};font-size:12px;color:#656d76;max-width:340px;">${esc(c.error || '')}</td>
    ${c.screenshot ? `<td style="${cell()};font-size:11px;"><a href="screenshots/${esc(c.screenshot)}" target="_blank">shot</a></td>` : `<td style="${cell()};font-size:11px;color:#9a9a9a;">—</td>`}
  </tr>`;
}
```

## 常見錯誤及避免方法
- **錯誤**：表格內容未正確轉義，導致 HTML 結構損壞。
  **解決方法**：使用 `esc()` 函數對所有動態內容進行轉義。
- **錯誤**：鏈接路徑錯誤，導致資源無法加載。
  **解決方法**：確保所有相對路徑根據 HTML 文件的位置正確設置。