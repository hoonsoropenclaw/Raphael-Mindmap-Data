# Visual Regression with Ignored Regions

## 說明...
此技能涉及使用 JavaScript 和 Canvas 來捕獲頁面截圖，並比較當前狀態與基準狀態的差異。同時，支持在比較時忽略特定區域（例如，時鐘組件）。

## 關鍵代碼片段或模式
```javascript
// 捕獲頁面截圖並繪製到 canvas
function snapStageToCanvas(canvas) {
  const ctx = canvas.getContext('2d');
  ctx.drawImage(document.querySelector('.snap-stage'), 0, 0, canvas.width, canvas.height);
}

// 比較兩個 canvas 的差異
function compareCanvases(canvas1, canvas2) {
  const ctx1 = canvas1.getContext('2d');
  const ctx2 = canvas2.getContext('2d');
  const imageData1 = ctx1.getImageData(0, 0, canvas1.width, canvas1.height);
  const imageData2 = ctx2.getImageData(0, 0, canvas2.width, canvas2.height);
  let diffPixels = 0;
  for (let i = 0; i < imageData1.data.length; i += 4) {
    if (imageData1.data[i] !== imageData2.data[i] ||
        imageData1.data[i + 1] !== imageData2.data[i + 1] ||
        imageData1.data[i + 2] !== imageData2.data[i + 2]) {
      diffPixels++;
    }
  }
  return diffPixels;
}
```

## 常見錯誤及避免方法
- **錯誤**: 忽略區域未正確標記，導致比較時未忽略。
  **解決方法**: 確保所有需要忽略的區域都正確添加了 `data-vr-ignore` 屬性。
- **錯誤**: 比較時未考慮設備像素比，導致比較結果不準確。
  **解決方法**: 在捕獲截圖和比較時考慮設備像素比，使用 `devicePixelRatio` 進行調整。