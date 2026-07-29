# Mini YAML Parser

## 說明
此微技能用於解析簡單的 YAML 格式配置檔案，適用於需要從配置檔案中提取資料的場景。

## 關鍵程式碼片段
```python
def _coerce(val: str) -> Any:
    """字串 → 自動型別轉換"""
    if val.startswith('"') and val.endswith('"'):
        return val[1:-1]
    if val.startswith("'") and val.endswith("'"):
        return val[1:-1]
    if val.startswith("[") and val.endswith("]"):
        items = [x.strip().strip('"').strip("'") for x in val[1:-1].split(",")]
        return [x for x in items if x]
    if val.lower() in ("true", "false"):
        return val.lower() == "true"
    if val.lower() in ("null", "none", "~", ""):
        return None
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    return val
```

## 常見錯誤及避免方法
1. **錯誤處理**: 當配置檔案包含註解或格式不規範時，可能導致解析錯誤。應在解析前清理註解並驗證格式。
2. **型別轉換**: 確保字串能正確轉換為目標型別，例如處理 `null` 或 `None` 時需特別注意。