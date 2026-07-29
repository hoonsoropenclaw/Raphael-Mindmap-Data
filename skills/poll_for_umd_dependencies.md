# Poll for UMD Dependencies

## 說明...
由於 UMD 依賴的加載順序和時間可能不確定，需要輪詢檢查所有必要的全局變量是否已加載，然後再啟動應用程序。

## 關鍵代碼片段或模式
```javascript
function checkDependencies() {
  const RF = window.ReactFlowCore;
  const RFB = window.ReactFlowBackground;
  const RFC = window.ReactFlowControls;
  const RFM = window.ReactFlowMinimap;

  if (!RF || !RFB || !RFC || !RFM) {
    setTimeout(checkDependencies, 100);
    return;
  }

  // 啟動應用程序
  compileAndRun();
}
checkDependencies();
```