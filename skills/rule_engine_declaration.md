# Rule Engine Declaration

## 说明
使用声明式规则引擎来匹配文件系统事件并执行相应的动作。规则以 `dataclass` 的形式定义，易于管理和扩展。

## 关键代码片段
```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class Rule:
    name: str
    description: str
    path_pattern: str
    event_type: str
    action: Callable

class AutomationEngine:
    def __init__(self, monitor, stats):
        self.monitor = monitor
        self.stats = stats
        self.rules = []

    def add_rule(self, rule: Rule):
        self.rules.append(rule)
        self.monitor.subscribe(rule, self.trigger_rule)

    def trigger_rule(self, rule: Rule, event: FSEvent):
        if rule.matches(event):
            rule.action(event)
```

## 常见错误及避免方法
- **错误**: 规则匹配逻辑错误，导致意外的动作执行。
  **解决方法**: 在规则匹配函数 `matches` 中添加详细的日志记录，确保规则按预期工作。
- **错误**: 规则引擎性能问题。
  **解决方法**: 对规则进行优化，例如使用索引或缓存来加速匹配过程。