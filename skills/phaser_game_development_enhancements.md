# Phaser Game Development Enhancements

## Overview
This document covers essential micro-skills for enhancing Phaser game development, focusing on WebGL configuration, dynamic physics debugging with Matter.js, lazy initialization of Graphics objects, and event error analysis using automation tools.

---

## 1. Phaser WebGL Context Setup

### Purpose
Configure the WebGL context in Phaser to enable screenshot capabilities in headless environments by setting `preserveDrawingBuffer` to `true`.

### Key Implementation

```javascript
callbacks: {
  postBoot: (game) => {
    if (game.renderer && game.renderer.gl) {
      const ctx = game.renderer.gl;
      const ext = ctx.getContextAttributes && ctx.getContextAttributes();
      if (ext && ext.preserveDrawingBuffer !== true) {
        console.log('[gl] preserveDrawingBuffer =', ext.preserveDrawingBuffer);
      }
    }
  }
},
render: { preserveDrawingBuffer: true },
```

### Common Errors and Prevention

- **Error**: `preserveDrawingBuffer` is not set correctly, causing screenshot failures.
  - **Solution**: Ensure `preserveDrawingBuffer: true` is explicitly set during Phaser initialization.
  
- **Error**: Lack of WebGL support in headless environments.
  - **Solution**: Use a headless browser or simulator that supports WebGL, such as Headless Chrome.

---

## 2. Matter Physics Debug Toggle

### Purpose
Enable dynamic switching of the Matter physics engine's debug mode in Phaser by listening to UI elements like checkboxes.

### Key Implementation

```javascript
const dbg = document.getElementById('chk-debug');
dbg.addEventListener('change', () => {
  const v = dbg.checked;
  scene.matter.world.drawDebug = v;
  if (v) {
    if (!scene.matter.world.debugGraphic) {
      scene.matter.createDebugGraphic();
    }
    scene.matter.world.debugGraphic.setDepth(1000);
    scene.matter.world.debugGraphic.clear();
  } else {
    if (scene.matter.world.debugGraphic) {
      scene.matter.world.debugGraphic.clear();
    }
  }
  scene.log(`<b>debug</b> <i>${v ? 'on' : 'off'}</i>`, 'event');
});
```

### Common Errors and Prevention

- **Error**: Debug graphics are not cleared when switching back to `false`, leading to memory leaks or visual glitches.
  - **Solution**: Always clear the debug graphics when disabling the debug mode.
  
- **Error**: `createDebugGraphic` method is unavailable due to Phaser version differences.
  - **Solution**: Verify the Phaser version and refer to the official documentation for the appropriate method to create debug graphics.

---

## 3. Phaser Graphics Lazy Initialization

### Purpose
Delay the initialization of Graphics objects in Phaser until the first update frame to prevent errors caused by calling `this.add.graphics()` before the scene is fully initialized.

### Key Implementation

```javascript
// Delay creation of Graphics object in update()
if (!this.debugG && this.add && typeof this.add.graphics === 'function') {
  try { this.debugG = this.add.graphics().setDepth(1000); } catch(e){}
}
if (this.debugG && this.debugG.visible) {
  this.debugG.clear();
  this.debugG.lineStyle(1, 0x7cf0c8, 0.6);
  // Draw custom debug outlines
}
```

### Common Errors and Prevention

- **Error**: `this.add` is not ready, causing `this.add.graphics()` to throw an error.
  - **Solution**: Initialize the Graphics object in the first update frame of the scene.
  
- **Error**: Graphics object is not set with the correct depth or visibility.
  - **Solution**: Ensure the Graphics object's depth and visibility properties are set after initialization.

---

## 4. Phaser Matter Physics Event Debugging

### Purpose
Use the Playwright automation tool to capture and analyze event errors triggered by the Matter physics engine in Phaser games.

### Key Implementation

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
        # Reproduce: debug toggle multiple times
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

### Common Errors and Prevention

- **Error**: Error information is incomplete or difficult to interpret.
  - **Solution**: Use `console.trace()` to obtain the call stack information of the error.
  
- **Error**: Playwright fails to capture errors correctly.
  - **Solution**: Ensure that the browser options for Playwright are set correctly and that the event listeners are properly configured.

---

## Summary
By mastering these micro-skills, developers can enhance their Phaser game development process, ensuring robust WebGL configurations, efficient physics debugging, optimized Graphics object initialization, and effective error analysis using automation tools.