# WebDriver Manager Chrome Setup

## 说明...
1. 使用 `webdriver-manager` 自动下载 Chrome 浏览器对应的 chromedriver。
2. 验证下载的 Chrome 和 chromedriver 版本是否匹配。
3. 处理无 root 权限时无法使用 `apt` 安装的替代方案。

## 关键代码片段
```python
from webdriver_manager.chrome import ChromeDriverManager
m = ChromeDriverManager().install()
print('driver path:', m)
```

## 常见错误及解决方法
- **错误**: `chromedriver` 与 Chrome 浏览器版本不匹配。
  **解决方法**: 使用 `webdriver-manager` 自动管理版本，避免手动下载导致的版本不匹配问题。
- **错误**: 权限不足，无法下载或安装。
  **解决方法**: 使用用户级别的安装方式，例如指定下载路径到用户目录，避免需要 root 权限。