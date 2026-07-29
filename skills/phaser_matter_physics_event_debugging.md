# Phaser Matter Physics Event Debugging

## 說明...
此技能涉及使用 Playwright 自動化工具來捕獲 Phaser 遊戲中由 Matter 物理引擎觸發的事件錯誤。通過監聽 `pageerror` 和 `console` 事件，收集錯誤信息並進行分析，以診斷和修復問題。

## 關鍵代碼片段
```python
async def main():
    errs = []
    console = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
        page = await (await browser.new_context(viewport={'width':1280,'height':760})).new_page()
        page.on('pageerror', lambda e: errs.append({'name': e.name, 'msg': e.message, 'stack': e.stack}))
        page.on('console', lambda m: console.append(f'[{m.type}] {m.text}') if m.type in ('error','warning') else None)
        await page.goto(f'http://127.0.0.1:{PORT}/index.html', wait_until='load', timeout=20000)
        await page.wait_for_function("() => window.__game && window.__game.scene.keys.Main && window.__game.scene.keys.Main.sys.isActive()", timeout=20000)
        await page.wait_for_timeout(2000)
        # 重現：debug toggle 多次
        await page.click('#chk-debug')
        await page.wait_for_timeout(500)
        await page.click('#chk-debug')
        await page.wait_for_timeout(500)
        await browser.close()
    print('page errors:', len(errs))
    for e in errs: print(e)
    print('
console errors/warnings:')
    for c in console: print(c)
```

## 常見錯誤及避免方法
- **錯誤**: 錯誤信息不完整或難以解讀。
  **解決方法**: 使用 `console.trace()` 來獲取錯誤的調用堆棧信息。
- **錯誤**: Playwright 無法正確捕獲錯誤。
  **解決方法**: 確保 Playwright 的瀏覽器選項設置正確，並且事件監聽器已正確設置。