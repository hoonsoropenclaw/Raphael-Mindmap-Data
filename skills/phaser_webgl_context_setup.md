# Phaser WebGL Context Setup

## 說明...
此技能涉及在 Phaser 遊戲初始化後配置 WebGL 上下文以允許在無頭環境中進行截屏。具體來說，通過設置 `preserveDrawingBuffer` 為 `true`，確保 WebGL 緩衝區的內容可以被讀取。

## 關鍵代碼片段
```javascript
callbacks: {
  postBoot: (game) => {
    if (game.renderer && game.renderer.gl) {
      const ctx = game.renderer.gl;
      const ext = ctx.getContextAttributes && ctx.getContextAttributes();
      if (ext && ext.preserveDrawingBuffer !== true) {
        console.log('[gl] preserveDrawingBuffer =', ext.preserveDrawingBuffer);
      }
    }
  }
},
render: { preserveDrawingBuffer: true },
```

## 常見錯誤及避免方法
- **錯誤**: `preserveDrawingBuffer` 未正確設置，導致截屏失敗。
  **解決方法**: 確保在初始化 Phaser 時明確設置 `preserveDrawingBuffer: true`。
- **錯誤**: 在無頭環境中缺少 WebGL 支持。
  **解決方法**: 使用支持 WebGL 的無頭瀏覽器或模擬器，例如 Headless Chrome。