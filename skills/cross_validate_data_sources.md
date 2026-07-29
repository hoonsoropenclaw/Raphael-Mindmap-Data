# Cross Validate Data Sources

## 目的
确保来自不同数据源的数据一致性，提高数据的可靠性和准确性。

## 关键代码或模式
```python
def cross_validate(api_data: list[ExtractedItem], html_data: list[ExtractedItem]) -> list[ExtractedItem]:
    merged_data = {item.id: item for item in api_data}
    for item in html_data:
        if item.id in merged_data:
            merged_data[item.id].merge(item)
        else:
            merged_data[item.id] = item
    return list(merged_data.values())
```

## 常见错误及避免方法
- **错误**: 数据源之间的数据格式不一致，导致合并失败。
  **避免方法**: 在合并之前进行数据格式的标准化处理。
- **错误**: 缺乏对数据冲突的处理策略，导致数据丢失或错误。
  **避免方法**: 制定明确的数据冲突解决策略，如优先使用某一数据源的数据或进行人工审核。