# Parallel Video Rendering

## 說明
此微技能利用 ThreadPoolExecutor 實現視頻的平行渲染，以提高處理效率。

## 關鍵程式碼片段
```python
from concurrent.futures import ThreadPoolExecutor

def render_videos(profiles, input_files, output_dir, workers=2):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        for profile in profiles:
            for input_file in input_files:
                futures.append(executor.submit(render_single_video, profile, input_file, output_dir))
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Error rendering video: {e}")
```

## 常見錯誤及避免方法
1. **資源競爭**: 確保每個渲染任務之間的資源不會發生競爭，例如檔案寫入衝突。
2. **錯誤處理**: 在平行處理中，錯誤處理需特別注意，避免單一任務失敗影響整體流程。