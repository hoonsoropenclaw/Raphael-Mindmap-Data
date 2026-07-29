# Matter Physics Debug Toggle

## 說明...
此技能涉及在 Phaser 遊戲中動態切換 Matter 物理引擎的調試模式。通過監聽 UI 元素（如複選框）的變化，來啟用或禁用物理世界的調試視覺效果。

## 關鍵代碼片段
```javascript
const dbg = document.getElementById('chk-debug');
dbg.addEventListener('change', () => {
  const v = dbg.checked;
  scene.matter.world.drawDebug = v;
  if (v) {
    if (!scene.matter.world.debugGraphic) {
      scene.matter.createDebugGraphic();
    }
    scene.matter.world.debugGraphic.setDepth(1000);
    scene.matter.world.debugGraphic.clear();
  } else {
    if (scene.matter.world.debugGraphic) {
      scene.matter.world.debugGraphic.clear();
    }
  }
  scene.log(`<b>debug</b> <i>${v ? 'on' : 'off'}</i>`, 'event');
});
```

## 常見錯誤及避免方法
- **錯誤**: 切換回 `false` 時未正確清除調試圖形，導致內存洩漏或視覺錯誤。
  **解決方法**: 在禁用調試模式時，確保調試圖形被清除。
- **錯誤**: Phaser 版本差異導致 `createDebugGraphic` 方法不可用。
  **解決方法**: 檢查 Phaser 版本並參考官方文檔，使用適當的方法來創建調試圖形。