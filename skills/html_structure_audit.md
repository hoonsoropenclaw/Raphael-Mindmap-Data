# HTML Structure Audit

## 說明...
此技能用於檢查 HTML 文件中的標籤、ID 唯一性以及必要元素的存在性，確保頁面結構符合預期。

## 關鍵代碼片段或模式
```python
from html.parser import HTMLParser

class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.duplicates = set()
        self.required_ids = {"apiKey", "saveKeyBtn", ...}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.duplicates.add(attrs["id"])
            self.ids.add(attrs["id"])

    def audit(self):
        assert not self.duplicates, f"Duplicate IDs: {self.duplicates}"
        assert self.required_ids <= self.ids, f"Missing IDs: {self.required_ids - self.ids}"
```

## 常見錯誤及避免方法
- **錯誤**: 缺少必要的 ID 或標籤。
  **避免方法**: 在 `required_ids` 中明確列出所有必要的 ID，並在審計過程中檢查它們是否存在。
- **錯誤**: 重複的 ID。
  **避免方法**: 使用集合來跟踪已見過的 ID，並在發現重複時拋出錯誤。