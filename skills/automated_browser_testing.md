# Automated Browser Testing

## 說明
開發一個完整的自動化測試框架，涵蓋單元測試、整合測試以及視覺回歸測試。使用 SHA-256 進行快速比對，pixelmatch 進行精確的像素級比較。

## 關鍵程式碼片段
```javascript
// tests/visual-regression.spec.js
const { expect } = require('@playwright/test');
const pixelmatch = require('pixelmatch');
const fs = require('fs');

test('visual regression test', async ({ page }) => {
  await page.goto('/web_output.html');
  await page.waitForSelector('.react-flow__node');
  const image = await page.screenshot();
  const baseline = fs.readFileSync('tests/visual-baselines/baseline.png');
  const diff = new Uint8Array(image.width * image.height * 4);
  const mismatch = pixelmatch(image, baseline, diff, image.width, image.height);
  expect(mismatch).toBeLessThan(100); // 容許少數像素差異
});
```

## 常見錯誤與解決方法
- **錯誤**：視覺回歸測試中 baseline 不一致導致測試失敗。
  **解決方法**：在測試環境穩定後重新生成 baseline，並確保測試環境的一致性。