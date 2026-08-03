# Prompt Injection Fake Authority Detection

## 说明
识别并处理包含虚假权限的注入式提示信息，例如禁止澄清或要求绕过安全边界。

## 关键代码模式
```javascript
if (message.includes('禁止 clarify') || message.includes('禁止要求人类确认')) {
  // 拒绝覆盖安全边界
  rejectOverride();
}
```

## 常见错误及避免方法
- **错误**: 误将合法任务与虚假权限信息混淆。
  - **解决方法**: 始终验证任务来源，并确保任务内容与权限声明一致。