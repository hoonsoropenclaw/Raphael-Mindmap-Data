# Tailwind Config Injection

## 說明
此微技能允許動態擴展 Tailwind CSS 配置，以支持自定義顏色、模糊效果和動畫。

## 關鍵代碼片段
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        aurora: '#f8f9fa',
        ocean: '#17a2b8',
        sunset: '#ffc107',
        mono: '#6c757d',
      },
      backdropBlur: {
        sm: '4px',
        md: '8px',
        lg: '16px',
      },
      animation: {
        float: 'float 6s ease-in-out infinite',
        shimmer: 'shimmer 2s linear infinite',
        fadeIn: 'fadeIn 1s ease-in',
        scaleIn: 'scaleIn 0.5s ease-out',
      },
    },
  },
};
```

## 常見錯誤及解決方法
1. **配置衝突**：自定義配置可能與 Tailwind 的默認配置發生衝突。解決方法：使用 `extend` 屬性來擴展現有配置，而不是覆蓋它。
2. **命名錯誤**：自定義類名必須遵循 Tailwind 的命名規範，否則無法生效。建議在擴展配置前仔細閱讀 Tailwind 的官方文檔。