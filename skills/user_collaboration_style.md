# User Collaboration Style

## 說明...
此技能使 AI 能夠根據用戶的合作風格調整其互動方式，例如在用戶偏好自主決策時減少詢問，或在用戶需要詳細解釋時提供更多信息。

## 關鍵代碼片段或模式
```python
def adjust_interaction_style(user_preferences):
    if user_preferences.get("autonomy") == "high":
        # 減少詢問，增加自主決策
        reduce_clarifications()
    elif user_preferences.get("autonomy") == "low":
        # 增加詢問，提供詳細解釋
        increase_clarifications()
    else:
        # 默認中等互動風格
        set_default_interaction()
```

## 常見錯誤及避免方法
- **錯誤**: 未能準確識別用戶的合作風格。
  **解決方法**: 通過多輪互動收集用戶偏好，並動態調整策略。
- **錯誤**: 過度調整導致用戶不適應。
  **解決方法**: 逐步調整互動風格，並根據用戶反饋進行修正。