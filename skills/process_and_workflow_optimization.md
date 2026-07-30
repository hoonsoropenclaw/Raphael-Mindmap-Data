# 微技能文档: process_and_workflow_optimization

## 概述
`process_and_workflow_optimization` 微技能旨在优化工作流、产品和标准操作程序（SOP），以提高效率和实现自动化。本文档整合了从文档处理、日历集成到工作流自动化、性能优化以及 SOP 决策逻辑设计与验证的全面解决方案，确保流程高效、稳定地运行。

## 1. 文档处理与集成

### 1.1 高级 PDF 和 OCR 处理

#### 1.1.1 文本提取与 OCR 处理
- **目标**: 从 PDF 文件中提取文本，包括文本型和扫描/图像型 PDF。
- **技术**: 使用 PyMuPDF 进行文本提取，使用 Tesseract 进行 OCR 处理。
- **示例代码**:
  ```python
  import pymupdf
  from PIL import Image
  import pytesseract

  def extract_text_pymupdf(pdf_path):
      doc = pymupdf.open(pdf_path)
      return [page.get_text('text') for page in doc]

  def extract_text_via_ocr(pdf_path):
      doc = pymupdf.open(pdf_path)
      pages_text = []
      for page in doc:
          pix = page.get_pixmap()
          img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
          text = pytesseract.image_to_string(img, lang='chi_tra+eng')
          pages_text.append(text)
      return pages_text
  ```
- **常见问题与解决方案**:
  - **OCR 准确性低**: 预处理图像以提高对比度、调整大小或应用滤镜。使用特定语言的 OCR 模型。
  - **处理大型 PDF 低效**: 实现多线程或多进程处理多个页面。

#### 1.1.2 基于正则表达式的数据提取
- **目标**: 从非结构化文本中提取特定数据字段（如日期、ID、金额）。
- **示例代码**:
  ```python
  import re

  def extract_key_data(text):
      patterns = {
          'document_number': r'發文字號[:：]\s*(府授文號字第\d+號)',
          'roc_date': r'中華民國(\d{1,3})年(\d{1,2})月(\d{1,2})日',
          'iso_date': r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
          'amount': r'NT\$\s*\d{1,3}(,\d{3})*',
          'email': r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
          'phone': r'\(?\d{2,4}\)?[- \.]?\d{6,8}',
          'address': r'[台灣市縣鄉鎮區路號樓]\s*\d{1,5}[巷弄號樓]?',
      }
      extracted_data = {}
      for key, pattern in patterns.items():
          match = re.search(pattern, text)
          if match:
              extracted_data[key] = match.group(1)
      return extracted_data
  ```
- **常见问题与解决方案**:
  - **模式过于严格**: 使用更灵活的模式，包含可选组和替代分隔符。
  - **模式重叠**: 根据特异性对模式进行优先级排序并相应地排序。

#### 1.1.3 前端 UI 使用 PDF.js 和 Tesseract.js
- **目标**: 创建用户友好的界面，用于上传和处理 PDF，利用 PDF.js 进行渲染，使用 Tesseract.js 进行浏览器内 OCR。
- **示例代码**:
  ```html
  <!DOCTYPE html>
  <html lang="zh-Hant">
  <head>
      <meta charset="UTF-8">
      <title>PDF OCR Processing</title>
      <script type="module">
          import { getDocument } from 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.0.379/build/pdf.min.mjs';
          import Tesseract from 'https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js';
      </script>
  </head>
  <body>
      <input type="file" id="pdf-upload" accept="application/pdf">
      <canvas id="pdf-render"></canvas>
      <script>
          const upload = document.getElementById('pdf-upload');
          upload.addEventListener('change', (e) => {
              const file = e.target.files[0];
              const loadingTask = getDocument({ url: URL.createObjectURL(file) });
              loadingTask.promise.then(pdf => {
                  pdf.getPage(1).then(page => {
                      const viewport = page.getViewport({ scale: 1.5 });
                      const canvas = document.getElementById('pdf-render');
                      canvas.height = viewport.height;
                      canvas.width = viewport.width;
                      const renderContext = {
                          canvasContext: canvas.getContext('2d'),
                          viewport: viewport
                      };
                      page.render(renderContext);
                      Tesseract.recognize(canvas, 'chi_tra+eng').then(({ data: { text } }) => {
                          console.log(text);
                      });
                  });
              });
          });
      </script>
  </body>
  </html>
  ```
- **常见问题与解决方案**:
  - **CORS 问题**: 确保 PDF 由适当的 CORS 头提供或使用本地文件上传。
  - **大型 PDF 的性能问题**: 实现分页或延迟加载以处理渲染和 OCR 处理。

#### 1.1.4 使用 Playwright 自动化 PDF OCR 工作流
- **目标**: 自动化上传 PDF、提取文本、执行 OCR、提取特定字段并导出结果的过程。
- **示例代码**:
  ```javascript
  const { chromium } = require('playwright');

  (async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    await page.goto('http://localhost:8000');
    
    // 上传 PDF
    const [fileChooser] = await Promise.all([
      page.waitForEvent('filechooser'),
      page.click('#uploadButton')
    ]);
    await fileChooser.setFiles(['/path/to/sample.pdf']);
    
    // 等待 OCR 完成
    await page.waitForSelector('#ocrResult', { timeout: 60000 });
    
    // 提取文本
    const text = await page.$eval('#ocrResult', el => el.value);
    console.log('Extracted Text:', text);
    
    await browser.close();
  })();
  ```
- **常见问题与解决方案**:
  - **文件上传失败**: 确保文件路径正确，文件权限设置适当。
  - **OCR 处理超时**: 增加超时持续时间，优化 OCR 处理逻辑，或限制处理文件的大小。

## 2. 工作流与性能优化

### 2.1 异步处理
- **目标**: 避免在执行 I/O 操作时阻塞主线程。
- **技术**: 使用异步编程范式或线程池。
- **示例代码**:
  ```python
  import asyncio

  async def run_workflow(event, rule, state, dispatcher):
      try:
          reminder = await generate_reminder_async(event, rule)
          await dispatcher(reminder)
          state.mark_as_sent(reminder)
      except Exception as e:
          log_error(e)
          state.mark_as_failed(reminder)
  ```

### 2.2 线程池管理
- **目标**: 管理并发线程的数量，防止资源耗尽。
- **示例代码**:
  ```python
  from concurrent.futures import ThreadPoolExecutor

  def run_workflow(event, rule, state, dispatcher):
      with ThreadPoolExecutor(max_workers=5) as executor:
          future = executor.submit(process_event, event, rule, state, dispatcher)
          try:
              future.result(timeout=10)
          except Exception as e:
              log_error(e)
              state.mark_as_failed(reminder)
  ```

### 2.3 超时机制
- **目标**: 防止进程无限期挂起。
- **示例代码**:
  ```python
  import multiprocessing

  def run_workflow(event, rule, state, dispatcher):
      process = multiprocessing.Process(target=process_event, args=(event, rule, state, dispatcher))
      process.start()
      process.join(timeout=10)
      if process.is_alive():
          process.terminate()
          state.mark_as_failed(reminder)
      else:
          if process.exitcode == 0:
              state.mark_as_sent(reminder)
          else:
              state.mark_as_failed(reminder)
  ```

### 2.4 错误处理与日志记录
- **目标**: 诊断问题和维护系统稳定性。
- **示例代码**:
  ```python
  def run_workflow(event, rule, state, dispatcher):
      try:
          reminder = generate_reminder(event, rule)
          dispatcher(reminder)
          state.mark_as_sent(reminder)
      except TimeoutError:
          log_error("Workflow execution timed out")
          state.mark_as_failed(reminder)
      except Exception as e:
          log_error(f"Unhandled exception: {e}")
          state.mark_as_failed(reminder)
  ```

### 2.5 资源管理
- **目标**: 防止瓶颈，确保可扩展性。
- **示例代码**:
  ```python
  def run_workflow(event, rule, state, dispatcher):
      with open("log.txt", "a") as log_file:
          try:
              reminder = generate_reminder(event, rule)
              dispatcher(reminder)
              state.mark_as_sent(reminder)
              log_file.write("Reminder sent successfully\n")
          except