# Micro-Skill: software_development_anti_patterns

## Overview
This micro-skill focuses on identifying and mitigating common software development pitfalls and mistakes that can lead to program hangs or inefficiencies. Two primary areas of concern are infinite loops and blocking I/O operations.

---

## 1. Anti-Pattern: Infinite Loop

### Explanation
Infinite loops occur when a loop lacks a proper termination condition or when the condition is perpetually true, causing the program to hang indefinitely.

### Key Code Patterns

#### Problematic Example
```python
# 錯誤示例
while True:
    user_input = input('Enter something: ')
    if user_input == 'exit':
        break
```
- **Issue**: The loop lacks additional termination conditions or logic to ensure it can exit based on variable states beyond user input.

#### Corrected Example
```python
# 修正後
while True:
    user_input = input('Enter something: ')
    if user_input == 'exit':
        break
    # 添加適當的循環終止條件，例如基於其他變量或計數器
    if some_other_condition:
        break
```
- **Improvement**: Introduce additional termination conditions to ensure the loop can exit based on multiple factors.

### Common Mistakes and Prevention

- **Mistake**: Absence of a termination condition or a condition that is always true.
  - **Solution**: Always define clear termination conditions and ensure loop variables are updated appropriately within the loop.
  
- **Mistake**: Logical errors within the loop that prevent the condition from being met.
  - **Solution**: Carefully review the loop's internal logic to ensure the condition can be satisfied within a reasonable timeframe.

---

## 2. Anti-Pattern: Blocking I/O

### Explanation
Blocking I/O operations, such as unbounded file reads or network requests without timeout settings, can cause the program to hang due to waiting indefinitely for I/O operations to complete.

### Key Code Patterns

#### Problematic Synchronous I/O Example
```python
import requests

def fetch(url):
    response = requests.get(url)  # 無超時設置，可能導致無限掛起
    return response.text

fetch('https://example.com')
```
- **Issue**: The synchronous `requests.get` call lacks a timeout, which can cause the program to hang if the server does not respond.

#### Corrected Asynchronous I/O Example
```python
import asyncio
import aiohttp

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=10) as response:  # 设置超時時間
            return await response.text()

# 使用 asyncio 進行非阻塞 I/O
asyncio.run(fetch('https://example.com'))
```
- **Improvement**: Utilize asynchronous programming (e.g., `asyncio`) and set a timeout to prevent the program from hanging.

### Common Mistakes and Prevention

- **Mistake**: Using blocking I/O operations in a synchronous environment, causing the main thread to hang.
  - **Solution**: Adopt asynchronous programming models (e.g., `asyncio`) to perform non-blocking I/O operations.
  
- **Mistake**: Failing to set a timeout for network requests.
  - **Solution**: Always specify a reasonable timeout for network requests to avoid indefinite waits.

---

## Summary of Best Practices

- **Define Clear Termination Conditions**: Ensure all loops have well-defined exit conditions that can be met based on the program's state.
  
- **Update Loop Variables Appropriately**: Modify loop variables within the loop to ensure termination conditions can be satisfied.
  
- **Use Asynchronous I/O**: Leverage asynchronous programming techniques to prevent I/O operations from blocking the main thread.
  
- **Set Timeouts for Network Operations**: Always configure timeouts for network requests to avoid hanging the program due to unresponsive services.

By adhering to these practices, developers can avoid common pitfalls related to infinite loops and blocking I/O operations, leading to more robust and efficient software.