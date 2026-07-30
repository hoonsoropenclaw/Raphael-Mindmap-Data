# Manifest Validation

## 目的
确保测试规范文件（Manifest）符合预定的结构和规则，避免因配置错误导致的测试失败或安全漏洞。

## 关键代码模式
```python
def validate_manifest(manifest: dict, location: str) -> None:
    if 'id' not in manifest:
        raise ManifestError(f"{location} missing required field: id")
    if 'steps' not in manifest:
        raise ManifestError(f"{location} missing required field: steps")
    if len(manifest['steps']) == 0:
        raise ManifestError(f"{location} must have at least one step")
    
    # 验证唯一 ID
    ids = set()
    for step in manifest['steps']:
        if 'id' not in step:
            raise ManifestError(f"{location}.steps[{step['id']}] missing required field: id")
        if step['id'] in ids:
            raise ManifestError(f"{location}.steps[{step['id']}] duplicate ID")
        ids.add(step['id'])

    # 验证角色引用
    configured_roles = set(config.roles)
    for step in manifest['steps']:
        role = step.get('role')
        if role is not None and role not in configured_roles:
            raise ManifestError(f"{location}.steps[{step['id']}] references unknown role: {role}")
```

## 常见错误及避免方法
- **错误**：缺少必需字段。
  **解决方法**：在验证过程中明确检查所有必需字段。
- **错误**：重复的 ID。
  **解决方法**：使用集合（set）来跟踪已使用的 ID。
- **错误**：未知的角色引用。
  **解决方法**：将配置文件中定义的角色与 Manifest 中引用的角色进行比对。