# Dashboard Design and Development

## Overview
Design and implement an interactive dashboard for displaying test results and visual regression test differences. The dashboard should include baseline, latest, and diff images, along with relevant statistics and interactive tools.

## Key Features
- **Visual Regression Test Results**: Display baseline, latest, and diff images.
- **Interactive Tools**: Provide interactive features for users to compare and analyze images.
- **Summary Statistics**: Show overall test results and browser-specific summaries.
- **Component Cards**: Include component-specific information and statuses.

## Implementation Steps

### 1. HTML Structure
Create a self-contained HTML file that includes all necessary elements for the dashboard.

```html
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=1280">
  <title>Visual Regression Dashboard</title>
  <style>
    /* Glassmorphism 风格设计 */
    body {
      background: linear-gradient(135deg, var(--bg-1), var(--bg-2), var(--bg-3));
      color: var(--ink);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      min-height: 100vh;
      margin: 0;
      padding: 0;
    }
    header {
      background-color: rgba(255, 255, 255, 0.1);
      padding: 20px;
      text-align: center;
    }
    h1 {
      margin: 0;
      font-size: 2em;
    }
    p {
      margin: 10px 0 0 0;
      font-size: 1.2em;
    }
    .container {
      display: flex;
      flex-wrap: wrap;
      padding: 20px;
    }
    .card {
      background-color: rgba(255, 255, 255, 0.8);
      margin: 10px;
      padding: 20px;
      border-radius: 10px;
      flex: 1 1 300px;
    }
    .image-container {
      position: relative;
      width: 100%;
      height: 0;
      padding-bottom: 56.25%; /* 16:9 aspect ratio */
      overflow: hidden;
    }
    .image-container img {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      object-fit: contain;
    }
  </style>
</head>
<body>
  <header>
    <h1>Visual Regression Dashboard</h1>
    <p>使用 Playwright 实现的视觉回归测试系统</p>
  </header>
  <div class="container">
    <!-- Summary Statistics -->
    <div class="card">
      <h2>总体统计</h2>
      <p>通过: <span id="passed-count">0</span></p>
      <p>失败: <span id="failed-count">0</span></p>
      <p>总测试数: <span id="total-count">0</span></p>
    </div>
    <!-- Browser Summary -->
    <div class="card">
      <h2>浏览器摘要</h2>
      <ul id="browser-summary">
        <!-- Browser summaries will be injected here -->
      </ul>
    </div>
    <!-- Component Cards -->
    <div class="card">
      <h2>组件卡片</h2>
      <div id="component-cards">
        <!-- Component cards will be injected here -->
      </div>
    </div>
    <!-- Interactive Image Viewer -->
    <div class="card">
      <h2>交互式图像查看器</h2>
      <div class="image-container">
        <img id="diff-image" src="" alt="Diff Image">
      </div>
      <button id="prev-button">上一张</button>
      <button id="next-button">下一张</button>
    </div>
  </div>
  <script>
    // JavaScript for interactivity
    document.addEventListener('DOMContentLoaded', () => {
      // Load report data
      const report = loadReport();

      // Populate summary statistics
      document.getElementById('passed-count').textContent = report.summary.passed;
      document.getElementById('failed-count').textContent = report.summary.failed;
      document.getElementById('total-count').textContent = report.summary.total;

      // Populate browser summary
      const browserSummary = document.getElementById('browser-summary');
      report.browsers.forEach(browser => {
        const li = document.createElement('li');
        li.textContent = `${browser.name}: ${browser.status}`;
        browserSummary.appendChild(li);
      });

      // Populate component cards
      const componentCards = document.getElementById('component-cards');
      report.components.forEach(component => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `<h3>${component.name}</h3><p>状态: ${component.status}</p>`;
        componentCards.appendChild(card);
      });

      // Interactive image viewer
      const diffImage = document.getElementById('diff-image');
      let currentImageIndex = 0;
      const diffImages = report.diffImages;

      diffImage.src = diffImages[currentImageIndex];

      document.getElementById('prev-button').addEventListener('click', () => {
        currentImageIndex = (currentImageIndex - 1 + diffImages.length) % diffImages.length;
        diffImage.src = diffImages[currentImageIndex];
      });

      document.getElementById('next-button').addEventListener('click', () => {
        currentImageIndex = (currentImageIndex + 1) % diffImages.length;
        diffImage.src = diffImages[currentImageIndex];
      });
    });

    // Function to load report data
    function loadReport() {
      // Placeholder for loading report data
      return {
        summary: {
          passed: 10,
          failed: 2,
          total: 12
        },
        browsers: [
          { name: 'Chrome', status: 'Passed' },
          { name: 'Firefox', status: 'Failed' }
        ],
        components: [
          { name: 'Header', status: 'Passed' },
          { name: 'Footer', status: 'Failed' }
        ],
        diffImages: [
          'images/diff1.png',
          'images/diff2.png'
        ]
      };
    }
  </script>
</body>
</html>
```

### 2. Python Backend
Build a Python backend to generate the dashboard HTML.

```python
def build_web_output():
    # Load report data
    report = load_report()

    # Generate summary statistics
    summary_html = f"""
    <div class="card">
      <h2>总体统计</h2>
      <p>通过: <span id="passed-count">{report.summary.passed}</span></p>
      <p>失败: <span id="failed-count">{report.summary.failed}</span></p>
      <p>总测试数: <span id="total-count">{report.summary.total}</span></p>
    </div>
    """

    # Generate browser summary
    browser_summary_html = "<ul id='browser-summary'>"
    for browser in report.browsers:
        browser_summary_html += f"<li>{browser.name}: {browser.status}</li>"
    browser_summary_html += "</ul>"

    # Generate component cards
    component_cards_html = "<div id='component-cards'>"
    for component in report.components:
        component_cards_html += f"<div class='card'><h3>{component.name}</h3><p>状态: {component.status}</p></div>"
    component_cards_html += "</div>"

    # Generate interactive image viewer
    diff_images_html = ""
    for image in report.diff_images:
        diff_images_html += f'<img src="{image}" alt="Diff Image">'

    # Render template
    template = f"""
    <!doctype html>
    <html lang="zh-Hant">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=1280">
      <title>Visual Regression Dashboard</title>
      <style>
        /* Glassmorphism 风格设计 */
        body {{
          background: linear-gradient(135deg, var(--bg-1), var(--bg-2), var(--bg-3));
          color: var(--ink);
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          min-height: 100vh;
          margin: 0;
          padding: 0;
        }}
        /* 其他样式省略 */
      </style>
    </head>
    <body>
      <header>
        <h1>Visual Regression Dashboard</h1>
        <p>使用 Playwright 实现的视觉回归测试系统</p>
      </header>
      <div class="container">
        {summary_html}
        {browser_summary_html}
        {component_cards_html}
        <div class="card">
          <h2>交互式图像查看器</h2>
          <div class="image-container">
            {diff_images_html}
          </div>
          <button id="prev-button">上一张</button>
          <button id="next-button">下一张</button>
        </div>
      </div>
      <script>
        // JavaScript for interactivity
        document.addEventListener('DOMContentLoaded', () => {