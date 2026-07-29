# Game Development with Native Integration

## Target Skill Name
game_development_with_native_integration

## Target Summary
This micro-skill focuses on developing games using the Phaser framework and integrating them with native platform functionalities to enhance game features across multiple platforms, including Android and desktop environments.

## Key Components

### 1. Phaser WebGL Configuration for Native Integration

#### Purpose
Configure the WebGL context in Phaser to enable advanced features such as screenshot capabilities in headless environments and seamless integration with native platforms.

#### Key Implementation
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

#### Common Errors and Prevention
- **Error**: `preserveDrawingBuffer` is not set correctly, causing screenshot failures.
  - **Solution**: Ensure `preserveDrawingBuffer: true` is explicitly set during Phaser initialization.
- **Error**: Lack of WebGL support in headless environments.
  - **Solution**: Use a headless browser or simulator that supports WebGL, such as Headless Chrome.

### 2. Dynamic Physics Debugging with Matter.js

#### Purpose
Enable dynamic switching of the Matter physics engine's debug mode in Phaser to facilitate real-time debugging and visualization of physics interactions.

#### Key Implementation
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

#### Common Errors and Prevention
- **Error**: Debug graphics are not cleared when switching back to `false`, leading to memory leaks or visual glitches.
  - **Solution**: Always clear the debug graphics when disabling the debug mode.
- **Error**: `createDebugGraphic` method is unavailable due to Phaser version differences.
  - **Solution**: Verify the Phaser version and refer to the official documentation for the appropriate method to create debug graphics.

### 3. Lazy Initialization of Graphics Objects

#### Purpose
Delay the initialization of Graphics objects in Phaser until the first update frame to prevent errors caused by calling `this.add.graphics()` before the scene is fully initialized.

#### Key Implementation
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

#### Common Errors and Prevention
- **Error**: `this.add` is not ready, causing `this.add.graphics()` to throw an error.
  - **Solution**: Initialize the Graphics object in the first update frame of the scene.
- **Error**: Graphics object is not set with the correct depth or visibility.
  - **Solution**: Ensure the Graphics object's depth and visibility properties are set after initialization.

### 4. Event Error Analysis Using Automation Tools

#### Purpose
Use the Playwright automation tool to capture and analyze event errors triggered by the Matter physics engine in Phaser games, ensuring robust error handling and debugging.

#### Key Implementation
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

#### Common Errors and Prevention
- **Error**: Error information is incomplete or difficult to interpret.
  - **Solution**: Use `console.trace()` to obtain the call stack information of the error.
- **Error**: Playwright fails to capture errors correctly.
  - **Solution**: Ensure that the browser options for Playwright are set correctly and that the event listeners are properly configured.

### 5. Multi-Platform Native Development

#### Android Native Development
- **Purpose**: Create native Android applications with a focus on user interface design, system integration, and performance optimization.
- **Key Code Snippets/Patterns**:
  ```java
  public class MainActivity extends AppCompatActivity {
      @Override
      protected void onCreate(Bundle savedInstanceState) {
          super.onCreate(savedInstanceState);
          setContentView(R.layout.activity_main);
          // Example: Initialize UI components
          TextView textView = findViewById(R.id.textView);
          textView.setText("Hello, Android!");
      }
  }
  ```
- **Common Errors & Solutions**:
  - **Error**: UI layout issues.
    - **Solution**: Use Android Studio's Layout Inspector to debug and resolve layout problems.
  - **Error**: Performance bottlenecks.
    - **Solution**: Optimize code, use background threads for heavy tasks, and leverage Android Profiler to identify performance issues.

#### Cross-Platform Desktop Capture and Optimization
- **Purpose**: Capture screenshots or images from the desktop environment in a way that is compatible across different operating systems and handles headless environments gracefully.
- **Key Code Snippets/Patterns**:
  ```python
  import mss
  from PIL import Image

  def capture_screen() -> Image.Image:
      with mss.mss() as sct:
          monitor = sct.monitors[1]
          screenshot = sct.grab(monitor)
          return Image.frombytes('RGB', screenshot.size, screenshot.rgb)
  ```
- **Common Errors & Solutions**:
  - **Error**: Headless environments without a graphical desktop.
    - **Solution**: Implement fallback mechanisms, such as returning a 503 error or using a placeholder image, instead of allowing the application to crash.
  - **Error**: Inconsistent monitor indexing across operating systems.
    - **Solution**: Use `sct.monitors[1]` to target the primary monitor, which is generally consistent, or provide configurable options for monitor selection.

#### Conditional Logic Implementation
- **Purpose**: Implement robust conditional logic to handle diverse platform-specific behaviors and configurations.
- **Key Code Snippets/Patterns**:
  ```python
  import platform
  import sys

  def get_os_specific_behavior():
      current_os = platform.system()
      if current_os == "Windows":
          # Windows-specific implementation
          return "windows_behavior"
      elif current_os == "Darwin":
          # macOS-specific implementation
          return "macos_behavior"
      elif current_os == "Linux":
          # Linux-specific implementation
          return "linux_behavior"
      else:
          # Fallback for unsupported OS
          return "unsupported_os_behavior"

  def handle_platform_specifics():
      behavior = get_os_specific_behavior()
      if behavior == "windows_behavior":
          # Implement Windows-specific logic
          pass
      elif behavior == "macos_behavior":
          # Implement macOS-specific logic
          pass
      elif behavior == "linux_behavior":
          # Implement Linux-specific logic
          pass
      else:
          # Handle unsupported OS
          sys.exit("Unsupported operating system")
  ```
- **Common Errors & Solutions**:
  - **Error**: Missing or incorrect platform detection.
    - **Solution**: Use reliable libraries like `platform` to accurately detect the operating system.
  - **Error**: Incomplete handling of all possible platforms.
    - **Solution**: Always include a fallback mechanism for unsupported platforms to prevent application crashes.

#### Filesystem Monitoring
- **Purpose**: Monitor filesystem changes across different operating systems to enable real-time updates and responses.
- **Key Code Snippets/Patterns**:
  ```python
  import os
  import time
  import platform
  from watchdog.observers import Observer
  from watchdog.events import FileSystemEventHandler

  class MyEventHandler(File