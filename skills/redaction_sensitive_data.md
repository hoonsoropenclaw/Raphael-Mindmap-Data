# Redaction of Sensitive Data

## 目的
在处理日志、报告或任何文本输出时，自动识别并遮罩敏感信息，以防止数据泄露。

## 关键代码模式
```python
import re

_SENSITIVE_KEYS = re.compile(
    r"(?:password|passphrase|secret|api[_-]?key|token|authorization|cookie|"
    r"national[_-]?id|id[_-]?number|ssn|salary|bank|account[_-]?number|"
    r"date[_-]?of[_-]?birth|\bdob\b|email|phone|address)",
    re.IGNORECASE,
)

def redact_text(text: str) -> str:
    return _SENSITIVE_KEYS.sub(REDACTED, text)
```

## 常见错误及避免方法
- **错误**：误将非敏感数据识别为敏感数据。
  **解决方法**：使用精确的正则表达式，并结合上下文进行判断。
- **错误**：敏感数据未被识别。
  **解决方法**：定期更新敏感数据模式，并进行充分的测试。