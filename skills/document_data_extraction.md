# document_data_extraction

## 概述
`document_data_extraction` 是一个综合性的微技能，旨在从文档中提取关键数据。它结合了 PDF.js 文字提取、Tesseract.js OCR 识别以及基于正则表达式的字段解析技术，适用于各种类型的文档，包括包含文字层的 PDF 文件、扫描版 PDF 以及图像文件。

## 技术细节

### 1. PDF.js 文字提取

#### 说明
PDF.js 是一个用于在网页中渲染和操作 PDF 文件的 JavaScript 库。通过 PDF.js，可以提取 PDF 文件的文字层内容。

#### 关键代码片段
```javascript
// 等待 PDF.js 渲染完成
page.wait_for_function("typeof window.__hrPdf === 'object'");

// 上传 PDF 文件
page.set_input_files("#file", "/path/to/pdf");

// 等待提取按钮可点击并点击
page.wait_for_function("document.getElementById('btnExtract').disabled === false", timeout=60000);
page.click("#btnExtract");

// 等待 OCR 处理完成（如果需要）
page.wait_for_function("document.getElementById('eventCount').textContent !== '0'", timeout=120000);

// 提取文本内容
const text = page.text_content("#textLayerLabel");
```

#### 常见错误及避免方法
- **错误**: PDF.js 未能正确渲染 PDF 文件，导致文字提取失败。
  **解决方法**: 确保 PDF 文件是有效的，并且 PDF.js 库已正确加载。
- **错误**: 提取的文本内容为空或不符合预期。
  **解决方法**: 检查 PDF 文件是否包含文字层，或考虑使用 OCR 工具进行图像识别。

### 2. Tesseract.js OCR 识别

#### 说明
Tesseract.js 是一个在浏览器中运行的 OCR 库，可以将图像中的文字转换为可编辑的文本。适用于没有文字层的扫描版 PDF 或图像文件。

#### 关键代码片段
```javascript
// 上传图像文件
page.set_input_files("#file", "/path/to/image");

// 等待 OCR 处理完成
page.wait_for_function("document.getElementById('eventCount').textContent !== '0'", timeout=120000);

// 提取 OCR 结果
const ocrText = page.text_content("#ocrResult");
```

#### 常见错误及避免方法
- **错误**: OCR 识别结果不准确。
  **解决方法**: 确保上传的图像清晰，文字对比度高。必要时进行预处理，如灰度化、二值化等。
- **错误**: OCR 处理时间过长。
  **解决方法**: 优化图像分辨率，避免上传过大的图像文件。

### 3. 基于正则表达式的字段解析

#### 说明
通过正则表达式从文本中提取关键信息，如员工姓名、日期、时间、地点和备注等。适用于结构化或半结构化的文本数据。

#### 关键代码片段
```javascript
// 定义正则表达式模式
const NAME_RE = /(?:員工姓名|應徵者|面試者|Employee\s*Name|Candidate|面试者|Name)\s*[：:]?\s*([A-Za-z\u4e00-\u9fa5][A-Za-z\u4e00-\u9fa5\s]{1,20})/;
const DATE_RES = [{
  type: "到職",
  re: /(到職日期|報到日期|到職日|Start\s*Date|Report\s*Date)\s*[：:]?\s*(\d{3,4}[\/.\\-年]\d{1,2}[\/.\\-月]\d{1,2}日?)/i
}];

// 提取字段
const lines = text.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
const foundNames = [];
for (const ln of lines) {
  const m = ln.match(NAME_RE);
  if (m) foundNames.push([ln, m[1]]);
}
```

#### 常见错误及避免方法
- **错误**: 正则表达式匹配错误或不完整。
  **解决方法**: 仔细测试正则表达式，确保其覆盖所有可能的文本格式。
- **错误**: 跨人数据污染。
  **解决方法**: 使用明确的分隔符或锚点来分隔不同人的数据块。

## 综合应用

### 步骤概述
1. **上传文档**: 使用 PDF.js 或 Tesseract.js 上传并处理文档。
2. **提取文字**: 根据文档类型选择合适的提取方法（PDF.js 或 Tesseract.js）。
3. **解析字段**: 使用正则表达式从提取的文本中提取关键字段。
4. **错误处理**: 处理可能出现的错误，如 OCR 识别错误或正则匹配失败。

### 示例流程
```javascript
// 上传并提取 PDF 文字
page.set_input_files("#file", "/path/to/pdf");
page.wait_for_function("document.getElementById('btnExtract').disabled === false", timeout=60000);
page.click("#btnExtract");
page.wait_for_function("document.getElementById('eventCount').textContent !== '0'", timeout=120000);
const text = page.text_content("#textLayerLabel");

// 如果是图像，使用 Tesseract.js 进行 OCR
// page.set_input_files("#file", "/path/to/image");
// page.wait_for_function("document.getElementById('eventCount').textContent !== '0'", timeout=120000);
// const text = page.text_content("#ocrResult");

// 使用正则表达式解析字段
const NAME_RE = /(?:員工姓名|應徵者|面試者|Employee\s*Name|Candidate|面试者|Name)\s*[：:]?\s*([A-Za-z\u4e00-\u9fa5][A-Za-z\u4e00-\u9fa5\s]{1,20})/;
const DATE_RES = [{
  type: "到職",
  re: /(到職日期|報到日期|到職日|Start\s*Date|Report\s*Date)\s*[：:]?\s*(\d{3,4}[\/.\\-年]\d{1,2}[\/.\\-月]\d{1,2}日?)/i
}];

const lines = text.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
const foundNames = [];
for (const ln of lines) {
  const m = ln.match(NAME_RE);
  if (m) foundNames.push([ln, m[1]]);
}
```

## 总结
`document_data_extraction` 通过结合 PDF.js、Tesseract.js 和正则表达式解析技术，提供了一种高效且灵活的文档数据提取解决方案。根据具体的文档类型和应用场景，可以灵活选择合适的技术手段，以实现最佳的数据提取效果。