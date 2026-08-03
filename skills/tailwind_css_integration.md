# Tailwind CSS Integration

## 說明...
整合 Tailwind CSS 至前端專案，配置自定義主題、字體、顏色、陰影等擴展功能。

## 關鍵程式碼片段或模式...
```javascript
tailwind.config = {
  theme: {
    extend: {
      fontFamily: {
        display: ['Manrope', 'Noto Sans TC', 'sans-serif'],
        mono: ['DM Mono', 'ui-monospace', 'monospace']
      },
      colors: {
        night: '#07111f',
        ice: '#dff7ff',
        cyan: '#5de4ff',
        mint: '#65f5c8',
        coral: '#ff8f88'
      },
      boxShadow: {
        glass: '0 24px 80px rgba(0, 10, 28, .38)',
        glow: '0 0 0 1px rgba(93,228,255,.16), 0 16px 60px rgba(57,203,255,.16)'
      }
    }
  }
}
```

## 常見錯誤及避免方法...
- **錯誤**：未正確配置 `tailwind.config.js`，導致自定義樣式無法生效。
  **解決方法**：確保 `tailwind.config.js` 的 `theme.extend` 部分正確設置，並重新啟動 Tailwind CLI 以應用更改。
- **錯誤**：字體未正確載入，導致字體無法顯示。
  **解決方法**：確認字體的 CSS 連結正確，並檢查瀏覽器控制台是否有載入錯誤。