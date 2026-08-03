# Visual Regression with Pillow

## 說明...
利用 Pillow 庫進行圖像的像素級別比較，以捕捉 UI 的視覺變化。

## 關鍵程式碼片段或模式
```python
from PIL import Image, ImageChops

def compare_images(baseline_path, current_path, diff_path):
    baseline = Image.open(baseline_path).convert('RGBA')
    current = Image.open(current_path).convert('RGBA')
    diff = ImageChops.difference(current, baseline)
    if diff.getbbox():
        diff.save(diff_path)
        return True
    return False
```

## 常見錯誤及避免方法
- **錯誤**：圖像大小不一致導致比較失敗。
  **解決方法**：在比較前強制將圖像調整為相同大小，或檢查截圖過程中是否有動態內容影響圖像尺寸。
- **錯誤**：圖像格式不支持。
  **解決方法**：確保所有圖像均為 PNG 格式，或在比較前進行格式轉換。