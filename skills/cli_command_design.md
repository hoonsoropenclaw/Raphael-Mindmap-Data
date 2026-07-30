# cli_command_design

## 說明...
設計並實現命令行工具的子命令，如 `fetch`, `batch`, `parse`, `design`。每個子命令負責不同的功能，並且可以接受不同的參數。

## 關鍵代碼片段或模式
```python
import argparse

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    # Fetch subcommand
    parser_fetch = subparsers.add_parser('fetch', help='Fetch data from a URL')
    parser_fetch.add_argument('url', help='URL to fetch')
    parser_fetch.add_argument('--mode', choices=['table', 'list', 'auto', 'images'], default='auto', help='Extraction mode')
    parser_fetch.add_argument('--out-path', help='Output file path')

    # Other subcommands...

    return parser
```

## 常見錯誤及避免方法
- **錯誤**：子命令之間的參數衝突，導致解析錯誤。
  - **解決方法**：為每個子命令定義獨立的參數集，並使用 `argparse` 的子解析器功能來管理。

- **錯誤**：缺少必需的參數時未提供有用的錯誤信息。
  - **解決方法**：使用 `argparse` 的 `required=True` 參數，並提供清晰的錯誤消息。