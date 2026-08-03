# Tailwind Config Injection

## 說明...
### 目的
允許動態注入自定義的 Tailwind CSS 配置，如主題顏色、字體、動畫等，以擴展默認主題。

### 關鍵代碼片段或模式
```javascript
// 自定義 Tailwind 配置
const customConfig = {
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef2ff',
          100: '#e0e7ff',
          // ...其他顏色
        },
        glass: {
          50: 'rgba(255,255,255,0.55)',
          // ...其他透明度
        },
      },
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        // ...其他大小
      },
      animations: {
        aurora: 'aurora 18s ease infinite',
        // ...其他動畫
      },
    },
  },
};

// 將配置應用到 Tailwind
tailwind.config(customConfig);
```

### 常見錯誤及避免方法
- **錯誤**：自定義配置語法錯誤，導致 Tailwind 編譯失敗。
  **解決方法**：使用 ESLint 或其他靜態分析工具檢查配置文件的語法，並參考官方文檔進行配置。
- **錯誤**：忘記將自定義配置應用到 Tailwind，導致配置無效。
  **解決方法**：確保在應用 Tailwind CSS 之前正確注入自定義配置。