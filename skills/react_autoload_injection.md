# React Autoload Injection

## 說明...
此技能涉及在 React 應用中通過 URL 查詢參數（如 `autoload=1`）自動載入和注入文件。主要步驟包括：
1. 解析 URL 查詢參數以檢測是否啟用自動載入。
2. 使用 `fetch` 從指定端點獲取 base64 編碼的圖片數據。
3. 將圖片數據轉換為 `File` 對象。
4. 模擬文件輸入的 `change` 事件，將文件注入到 React 的狀態中。

## 關鍵代碼片段...
```javascript
if (new URLSearchParams(location.search).get('autoload') === '1') {
  window.addEventListener('load', async () => {
    const resp = await fetch('/test_b64.json');
    const { dataUrl, filename } = await resp.json();
    const blob = await (await fetch(dataUrl)).blob();
    const file = new File([blob], filename, { type: blob.type });
    const dt = new DataTransfer();
    dt.items.add(file);
    const input = document.querySelector('.inspector input[type="file"]');
    if (input) {
      Object.defineProperty(input, 'files', { value: dt.files, configurable: true });
      input.dispatchEvent(new Event('change', { bubbles: true }));
    }
  });
}
```

## 常見錯誤及避免方法...
- **CORS 問題**: 在 `file://` 協議下運行時，`fetch` 可能會因跨域問題失敗。解決方法是使用本地 HTTP 服務器來提供文件。
- **React 狀態更新異步性**: 注入文件後，React 狀態更新是異步的，可能需要使用 `setTimeout` 或 `Promise` 來確保狀態已更新後再進行後續操作。
- **文件輸入元素未找到**: 如果文件輸入元素未正確加載或選擇器錯誤，可能導致無法注入文件。應確保選擇器準確並在 DOM 加載完成後執行注入操作。