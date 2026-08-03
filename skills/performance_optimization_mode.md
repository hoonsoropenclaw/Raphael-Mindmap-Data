# Performance Optimization Mode

## 說明...
此微技能涵蓋多種前端效能優化技術，包括資源預載、減少重排和重繪、以及使用現代 CSS 技術來提升渲染效能。

## 關鍵程式碼片段或模式
```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preload" as="font" type="font/woff2" href="..." crossorigin />
```

## 常見錯誤及避免方法
- **錯誤**：未使用資源預載技術，導致資源加載延遲。
  **解決方法**：使用 `preconnect` 和 `preload` 來提前加載關鍵資源。
- **錯誤**：過度使用 CSS 動畫，導致性能問題。
  **解決方法**：僅在必要時使用動畫，並使用 `will-change` 和 `transform` 來優化動畫性能。