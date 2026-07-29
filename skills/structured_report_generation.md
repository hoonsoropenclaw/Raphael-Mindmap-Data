# Structured Report Generation

## 說明
此微技能生成結構化的 JSON 格式渲染報告，記錄每個渲染任務的狀態、嘗試次數、持續時間、檔案大小和錯誤訊息。

## 關鍵程式碼片段
```python
import json

def generate_report(jobs):
    report = {"jobs": []}
    for job in jobs:
        report["jobs"].append({
            "status": job.status,
            "attempts": job.attempts,
            "duration_sec": job.duration_sec,
            "bytes": job.bytes,
            "error_msg": job.error_msg
        })
    with open("render_report.json", "w") as f:
        json.dump(report, f, indent=2)
```

## 常見錯誤及避免方法
1. **數據一致性**: 確保報告中的數據與實際渲染結果一致，避免數據不同步。
2. **檔案格式**: 驗證生成的 JSON 檔案格式正確，避免因格式錯誤導致後續處理失敗。