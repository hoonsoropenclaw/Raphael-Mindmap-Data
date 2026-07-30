# Calendar Management System

## 說明...
此微技能提供基於規則的日程提醒管理功能，包括事件解析、規則匹配以及提醒生成。

## 關鍵代碼片段
```python
def evaluate_rules(events, rules, now, lookahead):
    reminders = []
    for event in events:
        for rule in rules:
            if matches_rule(event, rule):
                remind_at = calculate_remind_time(event, rule)
                if now <= remind_at < now + timedelta(seconds=lookahead):
                    reminders.append(reminder)
    return reminders
```

## 常見錯誤與解決方法
- **規則匹配錯誤**：確保關鍵詞匹配時考慮大小寫不敏感，並且處理事件描述中的特殊字符。
- **時間計算錯誤**：所有時間計算必須考慮時區，避免因時區不同導致的錯誤。