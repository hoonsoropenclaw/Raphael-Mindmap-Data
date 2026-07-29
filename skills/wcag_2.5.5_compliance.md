# WCAG 2.5.5 Compliance

## 說明...
此技能涉及確保應用程序中的所有觸控目標（如按鈕、輸入框等）符合 WCAG 2.5.5 標準，即最小尺寸為 44×44 像素。

## 關鍵代碼片段或模式
```diff
@@ -108,7 +108,7 @@
     }
 
     input,
-    select { min-height: 42px; padding: 0 11px; }
+    select { min-height: 44px; padding: 0 11px; }
     textarea { min-height: 160px; padding: 12px; resize: vertical; }
     select { color-scheme: dark; }
```

## 常見錯誤及避免方法
- **錯誤**：觸控目標尺寸小於 44×44 像素。
  **避免方法**：在 CSS 中設置適當的 min-height 和 min-width，並在測試中進行驗證。
- **錯誤**：觸控目標被其他元素遮擋或不可見。
  **避免方法**：使用瀏覽器的開發者工具檢查觸控目標的可見性和層級關係。