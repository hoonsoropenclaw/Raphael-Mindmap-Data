# Phaser Graphics Lazy Initialization

## 說明...
此技能涉及在 Phaser 場景的生命週期中延遲初始化 Graphics 對象，以避免在場景尚未完全啟動時調用 `this.add.graphics()` 導致的錯誤。通過在第一個更新幀中創建 Graphics 對象，確保 `this.add` 系統已準備就緒。

## 關鍵代碼片段
```javascript
// 在 update() 內延遲創建 Graphics 對象
if (!this.debugG && this.add && typeof this.add.graphics === 'function') {
  try { this.debugG = this.add.graphics().setDepth(1000); } catch(e){}
}
if (this.debugG && this.debugG.visible) {
  this.debugG.clear();
  this.debugG.lineStyle(1, 0x7cf0c8, 0.6);
  // 繪製自定義調試外框
}
```

## 常見錯誤及避免方法
- **錯誤**: `this.add` 未準備就緒，導致 `this.add.graphics()` 拋出錯誤。
  **解決方法**: 將 Graphics 對象的初始化延遲到場景的第一個更新幀中。
- **錯誤**: Graphics 對象未正確設置深度或可見性。
  **解決方法**: 確保在初始化後設置 Graphics 對象的深度和可見性屬性。