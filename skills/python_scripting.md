# Python Scripting with Advanced Features

## Target Skill: python_scripting

### Summary
This micro-skill focuses on creating Python scripts with advanced features, including command-line interfaces (CLI) and algorithms like the Fibonacci sequence. It covers using the `argparse` module for CLI, implementing the Fibonacci sequence through various methods (iterative, recursive with memoization, and generator-based), and best practices to avoid common errors.

---

## 1. Creating Python CLI Scripts

### Overview
Develop Python scripts that accept command-line arguments using the `argparse` module. This allows users to interact with the script dynamically by passing parameters at runtime.

### Key Code Snippets

```python
import argparse

def main() -> int:
    parser = argparse.ArgumentParser(
        description="計算費氏數列第 n 項 (F(0)=0, F(1)=1)",
        epilog="範例: python3 fibonacci.py -n 20",
    )
    parser.add_argument(
        "-n", "--n", type=int, default=20,
        help="要計算的項數 (預設 20, 僅適用於 iterative / recursive)",
    )
    parser.add_argument(
        "-m", "--method",
        choices=["iterative", "recursive", "generator", "all"],
        default="all",
        help="計算方法 (預設 all)",
    )
    args = parser.parse_args()
    # 根據 args.method 調用相應的函數
    ...
```

### Common Errors and Prevention

- **Error**: Command-line arguments are not parsed correctly, causing the script to fail.
  - **Solution**: Ensure that parameter names and types are set correctly in the `argparse` setup. Provide clear help messages for users.
  
- **Error**: Missing required arguments are not handled properly.
  - **Solution**: Use the `required` parameter in `argparse` or set default values. Provide clear error messages when necessary arguments are missing.

---

## 2. Implementing the Fibonacci Sequence

### Overview
Create a Python script to compute the Fibonacci sequence using multiple approaches: iterative, recursive (with memoization), and generator-based methods.

### Key Code Snippets

```python
from functools import lru_cache

def fib_iterative(n: int) -> int:
    """迭代版：O(n) 時間、O(1) 空間，最推薦的實作。"""
    if n < 0:
        raise ValueError("n 必須是非負整數")
    if n in (0, 1):
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

@lru_cache(maxsize=None)
def fib_recursive(n: int) -> int:
    """遞迴 + memoization：O(n) 時間、O(n) 空間。"""
    if n < 0:
        raise ValueError("n 必須是非負整數")
    if n in (0, 1):
        return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)

def fib_generator(limit: int):
    """生成器：無限串流，可指定上限。"""
    a, b = 0, 1
    count = 0
    while count < limit:
        yield a
        a, b = b, a + b
        count += 1
```

### Common Errors and Prevention

- **Error**: Recursive implementation without memoization leads to poor performance.
  - **Solution**: Use the `functools.lru_cache` decorator to implement memoization, which significantly improves the efficiency of the recursive approach.
  
- **Error**: The generator does not have a proper termination condition, causing infinite loops or memory leaks.
  - **Solution**: Set explicit loop conditions and limits within the generator to prevent infinite loops. For example, use a `limit` parameter to control the number of iterations.

---

## 3. Best Practices and Error Prevention

### 1. **Argument Parsing with `argparse`**
   - **Tip**: Always provide clear and descriptive help messages using the `help` parameter. This aids users in understanding how to use the script.
   - **Tip**: Use default values for optional arguments to ensure the script can run without mandatory user input.

### 2. **Fibonacci Implementation**
   - **Tip**: Prefer the iterative approach for simplicity and performance unless memoization is required.
   - **Tip**: When using recursion, always incorporate memoization to avoid redundant calculations and improve performance.

### 3. **Generator Usage**
   - **Tip**: Clearly define the scope and limits of the generator to prevent unintended behavior.
   - **Tip**: Use generators when dealing with large sequences or when memory efficiency is a priority.

### 4. **Error Handling**
   - **Tip**: Anticipate and handle potential errors, such as invalid input types or out-of-range values, by using try-except blocks.
   - **Tip**: Provide meaningful error messages to help users understand what went wrong and how to fix it.

---

By following these guidelines and utilizing the provided code snippets, you can create robust Python scripts with advanced features, ensuring both functionality and user-friendliness.