# Visual Regression with Pillow

## 說明...
此技能使用 Pillow 庫來比較兩個圖像的像素差異，並生成差異圖像和報告。適用於需要精確視覺回歸測試的場景。

## 關鍵代碼片段或模式
```python
from PIL import Image, ImageChops, ImageMath

def compare_images(baseline_path, current_path, diff_path):
    baseline = Image.open(baseline_path).convert('RGBA')
    current = Image.open(current_path).convert('RGBA')
    diff = ImageChops.difference(baseline, current)
    channel_max = ImageChops.lighter(
        ImageChops.lighter(diff.getchannel('R'), diff.getchannel('G')),
        ImageChops.lighter(diff.getchannel('B'), diff.getchannel('A'))
    )
    bbox = channel_max.getbbox()
    if not bbox:
        pixels = 0
    else:
        pixels = sum(1 for px in channel_max.getdata() if px != 0)
    if pixels > 0:
        visual = Image.new('RGBA', baseline.size, (255, 32, 80, 0))
        visual.putalpha(channel_max.point(lambda x: min(255, x * 4)))
        Image.alpha_composite(current, visual).save(diff_path)
    return {
        'diffPixels': pixels,
        'totalPixels': baseline.width * baseline.height,
        'ratio': pixels / (baseline.width * baseline.height) if baseline.width * baseline.height > 0 else 0,
        'diffImage': str(diff_path) if bbox else None
    }
```

## 常見錯誤及避免方法
- **錯誤**：圖像尺寸不匹配導致比較失敗。
  **解決方法**：在比較前檢查圖像尺寸是否一致，並在必要時進行縮放或裁剪。
- **錯誤**：差異閾值設置不合理。
  **解決方法**：根據具體需求調整 `MAX_DIFF_PIXELS` 和 `MAX_DIFF_RATIO` 參數，以平衡靈敏度和容錯性。