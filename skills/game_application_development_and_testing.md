# 游戏应用开发与测试

## 目标技能名称
game_application_development_and_testing

## 目标概述
本微技能专注于使用 Godot 引擎进行游戏开发，实现与原生平台的无缝整合，并进行全面的质量保证测试和验证，以确保游戏功能在多平台（如 Android 和桌面环境）上的稳定性和可靠性。

## 主要组成部分

### 1. Godot 项目初始化

#### 描述
- **项目结构初始化**：设置 Godot 项目的基础结构，包括资源目录和场景组织。
- **配置 `project.godot`**：在 `project.godot` 文件中定义必要的项目设置和配置，如窗口大小、渲染设置等。
- **Godot 版本管理**：指定并管理项目使用的 Godot 引擎版本，确保兼容性和稳定性。

#### 关键代码片段和模式
```gdscript
[application]
config/name="Native Automation Studio"
run/main_scene="res://main.tscn"
```

#### 常见错误及预防措施
- **错误**：项目路径配置错误导致启动失败。
  - **解决方案**：确保 `run/main_scene` 路径正确且场景存在。
- **错误**：由于 Godot 版本不匹配导致的不兼容问题。
  - **解决方案**：在 `project.godot` 中明确指定 Godot 版本，并使用兼容的 Godot 二进制文件。

---

### 2. Godot 中的原生 UI 设计

#### 描述
- **UI 结构构建**：利用 Godot 的 Control 节点构建 UI 层次结构。
- **布局、大小和对齐配置**：定义 UI 元素的位置、大小和对齐方式，确保在不同分辨率下的适应性。
- **自定义主题和样式**：实现个性化的主题和样式，以增强 UI 的视觉吸引力。

#### 关键代码片段和模式
```gdscript
var root := VBoxContainer.new()
root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT, Control.PRESET_MODE_MINSIZE, 24)
add_child(root)
```

#### 常见错误及预防措施
- **错误**：UI 元素重叠或布局错位。
  - **解决方案**：使用锚点和边距正确放置元素，并使用容器来组织层次结构。
- **错误**：UI 无法适应不同分辨率。
  - **解决方案**：实施相对布局设置（例如，锚点或拉伸模式），而不是使用固定的数值。

---

### 3. 工作流引擎集成

#### 描述
- **工作流解析**：解释以 JSON 格式提供的工作流定义。
- **步骤执行**：执行预定义的步骤，如文件 I/O 操作和延迟。
- **错误处理**：优雅地管理错误，并支持 `continue_on_error` 机制，以便在不影响工作流的情况下处理问题。

#### 关键代码片段和模式
```gdscript
func run_workflow(workflow_path: String) -> Dictionary:
    var workflow_data := parse_json(File.read(workflow_path))
    for step in workflow_data.steps:
        match step.type:
            "read_file":
                var content := File.read(step.path)
                # 处理内容
            "write_file":
                File.write(step.path, step.content)
            # 处理其他步骤类型
```

#### 常见错误及预防措施
- **错误**：由于格式不正确导致 JSON 解析失败。
  - **解决方案**：在解析之前实施 JSON 格式验证。
- **错误**：文件路径不正确或权限不足。
  - **解决方案**：验证路径的有效性，并确保应用程序在执行之前具有必要的权限。

---

### 4. Godot 无头模式 CLI 配置

#### 描述
- **无头模式执行**：以无头模式启动 Godot 应用程序，即不运行图形用户界面。
- **命令行参数传递**：通过命令行参数提供工作流定义和其他参数。
- **输出管理**：将输出结果定向到指定文件以进行日志记录和分析。

#### 关键代码片段和模式
```bash
./run.sh --cli workflows/health_check.json automation-output/result.json
```

#### 常见错误及预防措施
- **错误**：GUI 元素尝试在无头模式下渲染。
  - **解决方案**：在启动时检查应用程序是否以无头模式运行，并避免调用任何与 GUI 相关的函数。
- **错误**：命令行参数解析不正确。
  - **解决方案**：使用可靠的命令行解析库或方法，并包括参数验证。

---

### 5. Godot 中的集成测试

#### 描述
- **测试脚本开发**：创建测试脚本来验证应用程序的各种功能。
- **无头模式测试**：在无头模式下运行应用程序，并分析输出以确保正确性。
- **场景模拟**：模拟不同的场景和错误条件，以确保应用程序行为的健壮性。

#### 关键代码片段和模式
```bash
./tests/integration.sh
```

#### 常见错误及预防措施
- **错误**：测试环境配置错误导致测试失败。
  - **解决方案**：确保测试环境与生产环境一致，并使用虚拟化来隔离测试环境。
- **错误**：测试覆盖范围不足。
  - **解决方案**：开发全面的测试用例，涵盖所有主要功能和边缘情况。

---

### 6. Phaser WebGL 配置以实现原生集成

#### 目的
配置 Phaser 中的 WebGL 上下文，以启用高级功能，如无头环境中的屏幕截图功能，并实现与原生平台的无缝集成。

#### 关键实现
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

#### 常见错误及预防措施
- **错误**：`preserveDrawingBuffer` 设置不正确，导致屏幕截图失败。
  - **解决方案**：在 Phaser 初始化时明确设置 `preserveDrawingBuffer: true`。
- **错误**：无头环境中缺少 WebGL 支持。
  - **解决方案**：使用支持 WebGL 的无头浏览器或模拟器，例如 Headless Chrome。

---

### 7. 使用 Matter.js 进行动态物理调试

#### 目的
在 Phaser 中启用动态切换 Matter 物理引擎的调试模式，以促进实时调试和可视化物理交互。

#### 关键实现
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

#### 常见错误及预防措施
- **错误**：调试图形在切换回 `false` 时未清除，导致内存泄漏或视觉故障。
  - **解决方案**：在禁用调试模式时始终清除调试图形。
- **错误**：`createDebugGraphic` 方法由于 Phaser 版本差异而不可用。
  - **解决方案**：验证 Phaser 版本，并参考官方文档以获取创建调试图形的适当方法。

---

### 8. 图形对象的延迟初始化

#### 目的
将 Phaser 中图形对象的初始化延迟到第一个更新帧，以防止在场景完全初始化之前调用 `this.add.graphics()` 导致的错误。

#### 关键实现
```javascript
// 在 update() 中延迟创建 Graphics 对象
if (!this.debugG && this.add && typeof this.add.graphics === 'function') {
  try { this.debugG = this.add.graphics().setDepth(1000); } catch(e){}
}
if (this.debugG && this.debugG.visible) {
  this.debugG.clear();
  this.debugG.lineStyle(1, 0x7cf0c8, 0.6);
  // 绘制自定义调试轮廓
}
```

#### 常见错误及预防措施
- **错误**：`this.add` 尚未准备好，导致 `this.add.graphics()` 抛出错误。
  - **解决方案**：在场景的第一个更新帧中初始化图形对象。
- **错误**：图形对象的深度或可见性属性未正确设置。
  - **解决方案**：确保在初始化后设置图形对象的深度和可见性属性。

---

### 9. 使用自动化工具进行事件错误分析

#### 目的
使用 Playwright 自动化工具捕获和分析由 Phaser 游戏中的 Matter 物理引擎触发的事件错误，确保健壮的错误处理和调试。

#### 关键实现
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
        await page.wait_for_function("() => window.__game && window.__game.scene.keys.Main && window.__game.scene.keys.Main.sys.isActive()",