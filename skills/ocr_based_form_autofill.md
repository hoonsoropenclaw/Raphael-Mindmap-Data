# OCR-Based Form Auto-Fill

## 說明...

### 目的
實現基於 OCR 的自動填表功能，從上傳的圖片中提取文本並自動填入表單字段。

### 關鍵代碼片段
```javascript
function autoFillFields(ocrText) {
  const fields = [
    { key: 'name', pattern: /[\u4e00-\u9fa5]{2,4}|[A-Z][a-z]+\s+[A-Z][a-z]+/ },
    { key: 'company', pattern: /[\u4e00-\u9fa5A-Za-z0-9 ]{2,}(?:科技|公司|股份|有限公司|集團|Corp\.|Inc\.|Co\.|Ltd\.)/ },
    { key: 'title', pattern: /技術長|經理|總監|工程師|主任|Manager|Director|Engineer|CEO|CTO/ },
    { key: 'phone', pattern: /\+?\d{1,3}[-\s]?\d{1,4}[-\s]?\d{3,4}[-\s]?\d{3,4}/ },
    { key: 'email', pattern: /[\w.+-]+@[\w-]+\.[\w.-]+/ }
  ];

  const result = {};

  fields.forEach(field => {
    const match = ocrText.match(field.pattern);
    if (match) {
      result[field.key] = match[0];
    }
  });

  return result;
}
```

### 常見錯誤及避免方法
- **錯誤**：正則表達式無法正確匹配文本。
  **解決方法**：根據實際應用場景調整正則表達式，並進行充分的測試。
- **錯誤**：OCR 提取的文本格式不正確。
  **解決方法**：在填表前對提取的文本進行清洗和格式化處理。