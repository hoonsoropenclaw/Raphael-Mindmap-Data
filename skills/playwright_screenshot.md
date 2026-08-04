# Playwright Screenshot

## 說明...
使用 Playwright 的 `page.screenshot` 方法，可以針對網頁的特定元素或區域進行截圖，並將圖片保存到指定路徑。

## 關鍵程式碼片段
```javascript
await page.locator('#parallax').screenshot({ path: path.resolve('test-results/parallax-only.png') });
```

## 常見錯誤及避免方法
- **錯誤**: 截圖路徑錯誤或權限不足，導致無法保存圖片。
  **解決方法**: 確保目標路徑存在且有寫入權限，使用絕對路徑或 `path.resolve` 來避免路徑問題。
- **錯誤**: 元素定位失敗，導致截圖為空。
  **解決方法**: 確認元素選擇器正確，並在截圖前使用 `await page.waitForSelector` 確保元素已加載。