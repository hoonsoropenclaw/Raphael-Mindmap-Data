# Lazy Browser Launch

## 說明

此技能確保在所有目標頁面都能通過靜態解析時，完全不啟動瀏覽器。只有在靜態解析無法滿足資料需求時，才會啟動瀏覽器進行動態渲染，從而優化資源使用。

## 關鍵程式碼片段

```python
from hybrid_scraper.playwright_renderer import PlaywrightRenderer

async def render_if_needed(url, schema, renderer):
    if needs_dynamic_rendering(url, schema):
        async with renderer:
            return await renderer.render(url, schema)
    else:
        return await static_parse(url, schema)

def needs_dynamic_rendering(url, schema) -> bool:
    # 根據 schema 中的 wait_selector 和其他條件判斷是否需要動態渲染
    return True if schema.wait_selector else False
```

## 常見錯誤及避免方法

1. **錯誤：瀏覽器未正確啟動**
   - **原因**：瀏覽器啟動邏輯中的鎖或信號量使用不當。
   - **解決方法**：檢查 `PlaywrightRenderer` 中的鎖機制，確保瀏覽器啟動過程是線程安全的。

2. **錯誤：資源競爭導致性能問題**
   - **原因**：多個請求同時觸發瀏覽器啟動，導致資源競爭。
   - **解決方法**：使用信號量或鎖機制限制同時啟動的瀏覽器實例數量。