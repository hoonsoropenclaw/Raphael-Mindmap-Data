# Anti-Pattern: Blocking I/O

## 說明...
此微技能提供識別和修復阻塞 I/O 操作問題的方法，特別是在處理文件讀寫、網絡請求等操作時。

## 關鍵代碼片段
```python
import asyncio

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def main():
    ...
    data = await fetch_data(url)
    ...
```

## 常見錯誤與解決方法
- **阻塞操作在主線程中執行**：使用異步編程或線程池來處理阻塞操作，避免在主線程中執行。
- **缺乏錯誤處理**：添加適當的錯誤處理機制，處理 I/O 操作中的異常情況。