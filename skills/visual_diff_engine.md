# Visual Diff Engine

## 說明...
此技能用於比較網頁截圖的視覺差異，並生成差異報告。

## 關鍵代碼片段或模式
```javascript
function visualRow(c) {
  const isFail = c.status === 'fail' || c.status === 'size-mismatch' || c.status === 'pillow-divergence';
  const pixelPct = c.diffRatio != null ? (c.diffRatio * 100).toFixed(2) + '%' : '—';
  const pillowPct = c.pillowDiffRatio != null ? (c.pillowDiffRatio * 100).toFixed(2) + '%' : '—';
  return `<tr style="border-bottom:1px solid #eaeef2;${isFail ? 'background:#fff8f8;' : ''}">
    <td style="${cell()};font-family:ui-monospace,monospace;font-size:12px;">${esc(c.browser)}</td>
    <td style="${cell()};font-family:ui-monospace,monospace;font-size:12px;">${esc(c.page)}</td>
    <td style="${cell()};">${statusChip(c.status, VISUAL_STATUS)}</td>
    <td style="${cell()};font-size:12px;">${esc(pixelPct)}</td>
    <td style="${cell()};font-size:12px;">${esc(pillowPct)}</td>
    <td style="${cell()};font-size:11px;color:#9a9a9a;">${c.diffPixels != null ? c.diffPixels.toLocaleString() + ' px' : '—'}</td>
    ...
  </tr>`;
}
```

## 常見錯誤及避免方法
- **錯誤**：差異閾值設置不合理，導致誤報或漏報。
  **解決方法**：根據具體需求調整像素和 Pillow 差異的閾值，例如設置為 2% 和 2.5%。
- **錯誤**：忽略動態元素，導致不必要的差異。
  **解決方法**：使用遮罩策略，例如通過 `[data-mask="dynamic"]` 隱藏時間戳記等易變元素。