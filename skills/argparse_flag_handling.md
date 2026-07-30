# argparse_flag_handling

## 說明...
處理 argparse 中帶有可選短標誌（以 `-` 開頭）和長標誌（以 `--` 開頭）的參數。確保在短標誌為 `None` 時不會引發錯誤。

## 關鍵代碼片段或模式
```python
for short, long_flag, opts in _SHARED:
    # Each tuple: (primary_flag_or_None, alias_or_None, opts_dict).
    # Pass a list of positional flag strings; argparse ignores None entries.
    flags = [f for f in (short, long_flag) if isinstance(f, str) and f.startswith("-")]
    sp.add_argument(*flags, **opts)
```

## 常見錯誤及避免方法
- **錯誤**：當短標誌為 `None` 時，argparse 會將 `None` 作為選項字符串，導致錯誤。
  - **解決方法**：在添加參數之前，檢查短標誌是否為字符串並以 `-` 開頭。如果短標誌為 `None`，則僅添加長標誌。

- **錯誤**：迭代時未正確解包元組，導致參數順序錯誤。
  - **解決方法**：使用明確的變量名稱（如 `short`, `long_flag`, `opts`）來解包元組，並確保每個參數的位置正確。