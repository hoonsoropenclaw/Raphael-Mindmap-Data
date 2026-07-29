# Retry Mechanism

## 說明
此微技能實現了視頻渲染的重試機制，當渲染失敗時自動重試指定次數，以提高任務的成功率。

## 關鍵程式碼片段
```python
def render_with_retry(profile, input_file, output_dir, retries=2):
    attempt = 0
    while attempt <= retries:
        try:
            render_single_video(profile, input_file, output_dir)
            return True
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} failed with error: {e}")
    return False
```

## 常見錯誤及避免方法
1. **無限重試**: 設定合理的重試次數，避免因無限重試導致資源浪費。
2. **錯誤分類**: 根據錯誤類型決定是否需要重試，例如網絡錯誤可以重試，而語法錯誤則不需要。