# Babel Inline JSX Compilation

## 說明...

### 目的
將 HTML 文件中的 inline JSX 區塊提取出來，使用 Babel 編譯為標準的 JavaScript，以便在瀏覽器中運行。

### 關鍵代碼片段或模式
```python
import re, pathlib
html = pathlib.Path('/path/to/file.html').read_text()
# 使用正則表達式提取 <script type="text/babel"> 區塊
m = re.search(r'<script type="text/babel"[^>]*>(.*?)</script>', html, re.DOTALL)
assert m, "no inline babel script found"
js = m.group(1)
pathlib.Path('/tmp/babel_build/in.jsx').write_text(js)
```

### 常見錯誤及避免方法
- **錯誤**: 找不到 inline JSX 區塊。
  **解決方法**: 確認 HTML 文件中確實存在 `<script type="text/babel">` 區塊，並檢查正則表達式是否正確。
- **錯誤**: Babel 編譯失敗。
  **解決方法**: 確認 Babel 配置正確，並檢查 JSX 代碼是否存在語法錯誤。