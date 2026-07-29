# Responsive Design

## 說明
此技能涉及實現響應式設計，使應用在不同設備和屏幕尺寸下都能提供良好的用戶體驗。

## 關鍵代碼片段
```css
@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 520px) {
  .top {
    padding: 0 15px;
  }
}
```

## 常見錯誤及避免方法
- **佈局崩潰**：使用相對單位和彈性佈局來避免佈局崩潰。
- **資源加載問題**：優化資源以適應不同網絡條件。
- **可訪問性問題**：確保響應式設計不會影響應用的可訪問性。