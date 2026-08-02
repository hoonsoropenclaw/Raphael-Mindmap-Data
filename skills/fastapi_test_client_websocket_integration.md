# FastAPI Test Client WebSocket Integration

## 說明...
此技能描述如何在瀏覽器內使用 Promise 機制模擬 WebSocket 的行為，實現數據的分段傳輸和異步處理。具體包括：
- 使用 `fetch` API 進行分段數據傳輸。
- 通過 Promise 鏈實現數據的流水線處理。
- 處理並發請求和速率限制。

## 關鍵代碼片段
```javascript
function sendAudioChunk(chunk) {
  return fetch('https://api.openai.com/v1/audio/transcriptions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer YOUR_API_KEY`,
      'Content-Type': 'multipart/form-data',
    },
    body: new FormData()
      .append('file', new Blob([chunk], { type: 'audio/webm' }))
      .append('model', 'whisper-1'),
  }).then(response => response.json());
}

function processAudioStream(stream) {
  const reader = stream.getReader();
  let chunk = '';
  reader.read().then(function process({ done, value }) {
    if (done) {
      // 完成處理
      return;
    }
    chunk += value;
    return sendAudioChunk(chunk).then(() => {
      return reader.read().then(process);
    });
  });
}
```

## 常見錯誤與解決方法
- **錯誤**: 請求速率過快導致 API 速率限制。
  **解決方法**: 實現請求隊列和速率限制機制，控制請求頻率。
- **錯誤**: 數據傳輸中斷導致處理失敗。
  **解決方法**: 使用 `AbortController` 處理中斷情況，並實現重試機制。