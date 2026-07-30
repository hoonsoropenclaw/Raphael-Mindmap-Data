# Tailwind Config Extend

## 說明...
此技能涉及在 `tailwind.config.js` 中擴展自定義顏色、字體、動畫和其他設計 token，以實現高度定制的 UI 設計。

## 關鍵代碼片段或模式
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        amber: { ... },
        ink: { ... },
        glass: {
          tint: 'rgba(255, 248, 235, 0.06)',
          panel: 'rgba(255, 255, 255, 0.06)',
          deep: 'rgba(11, 15, 26, 0.45)',
          stroke: 'rgba(255, 255, 255, 0.10)',
          stroke2: 'rgba(255, 255, 255, 0.18)',
        },
        status: {
          approved: '#7fc89e',
          pending: '#f4c45f',
          rejected: '#e08282',
          draft: '#a5a8b5',
        },
      },
      backdropBlur: {
        xs: '2px',
        '2xl': '32px',
        '3xl': '48px',
      },
      boxShadow: {
        glassSm: '0 2px 8px rgba(0, 0, 0, 0.12)',
        glassMd: '0 4px 16px rgba(0, 0, 0, 0.2)',
        glassLg: '0 8px 24px rgba(0, 0, 0, 0.25)',
        glowAmber: '0 0 24px rgba(244, 159, 51, 0.5)',
      },
      keyframes: {
        drift: { ... },
        pulseSoft: { ... },
        shimmer: { ... },
        ticker: { ... },
        rise: { ... },
      },
    },
  },
  plugins: [],
}
```

## 常見錯誤及避免方法
- **錯誤**：忘記在 `extend` 塊中定義自定義屬性，導致工具類無法使用。
  **解決方法**：確保所有自定義屬性都放在 `extend` 塊中。
- **錯誤**：顏色名稱或鍵名拼寫錯誤，導致 CSS 無法正確生成。
  **解決方法**：仔細檢查拼寫並參考 Tailwind 官方文檔。