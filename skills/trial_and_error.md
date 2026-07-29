# Trial and Error

## 说明
此技能用于在面对未知问题时，通过反复尝试和修正错误来找到解决方案。

## 关键代码或模式
```python
def solve_problem(problem):
    while not is_solved(problem):
        attempt = generate_attempt(problem)
        if attempt.is_successful:
            return attempt.solution
        else:
            log_error(attempt.error)
```

## 常见错误及避免方法
- **错误**: 试错过程缺乏记录，导致重复错误。
  **避免方法**: 详细记录每次尝试的结果和错误，以便后续分析。