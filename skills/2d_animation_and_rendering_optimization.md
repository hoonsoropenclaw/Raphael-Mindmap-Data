# 2D Animation and Rendering Optimization for Phaser 3

## Overview

This micro-skill focuses on optimizing the 2D animation pipeline in Phaser 3, including techniques for custom node rendering and real-time monitoring of FPS and performance metrics. The goal is to enhance rendering efficiency, reduce performance bottlenecks, and ensure smooth animations in Phaser 3-based 2D games.

## Key Techniques

### 1. Spritesheet Handling

Efficiently manage and load spritesheets to optimize animation performance.

#### Loading Spritesheets

Use the `load.spritesheet` method to load horizontally arranged PNG strips. This ensures that individual frames are accessible at runtime.

```javascript
this.load.spritesheet('walk_sheet', 'assets/walk.png', { frameWidth: 32, frameHeight: 32, endFrame: 3 });
this.load.spritesheet('jump_sheet', 'assets/jump.png', { frameWidth: 32, frameHeight: 32, endFrame: 3 });
this.load.spritesheet('run_sheet', 'assets/run.png', { frameWidth: 32, frameHeight: 32, endFrame: 3 });
this.load.spritesheet('hit_sheet', 'assets/hit.png', { frameWidth: 32, frameHeight: 32, endFrame: 1 });
```

#### Common Errors and Solutions

- **Error**: Using `textures.addImage` in `preload` causes competition with WebGL initialization.
  - **Solution**: Use `load.image` or `load.spritesheet` to ensure texture uploads are controlled by the loader's internal queue.
  
- **Error**: Calling `tex.add(...)` on `ImageTexture` after `load.image` leads to missing frame metadata.
  - **Solution**: Use `load.spritesheet` during preloading and provide `frameWidth`, `frameHeight`, and `endFrame`.

### 2. Object Pooling

Implement object pooling to minimize garbage collection pressure from frequent sprite creation and destruction.

```javascript
const spritePool = this.add.group({
  defaultKey: 'walk_sheet',
  maxSize: 1000
});

const sprite = spritePool.get(x, y, 'walk_sheet', 0);
sprite.play('walk');
```

### 3. Container Batching

Utilize `Container` batching to group sprites and leverage the renderer’s ability to batch texture frames, thereby improving rendering efficiency.

```javascript
const container = this.add.container(0, 0);
container.add(sprite);
```

### 4. Off-screen Culling

Implement off-screen culling to enhance rendering performance by skipping the rendering of sprites that are not within the camera's view.

```javascript
const ticker = setInterval(() => {
  if (!game || !game.scene || game.isDestroyed) {
    clearInterval(ticker);
    return;
  }
  const s = game.scene.getScene('pipeline');
  if (!s || !s.scene || !s.scene.isActive()) return;
  try {
    s.events.emit('metrics:tick');
  } catch (_) {}
}, 500);
```

### 5. Custom Node Rendering

Customize node rendering to achieve specific visual effects, such as using linear gradient backgrounds and center-aligned text to differentiate node types.

#### Example: Applying Linear Gradient Background

```css
.node {
  background: linear-gradient(to right, #ff7e5f, #feb47b);
  text-align: center;
  padding: 20px;
  border-radius: 8px;
}
```

### 6. FPS and Performance Monitoring

Implement real-time monitoring of FPS and rendering times to quickly identify performance bottlenecks.

#### Displaying FPS and Rendering Time

```javascript
const fpsText = this.add.text(10, 10, '', { font: '16px Courier', fill: '#ffffff' });

this.game.loop.add(() => {
  const fps = this.game.loop.actualFps.toFixed(2);
  const renderTime = this.game.loop.delta.toFixed(2);
  fpsText.setText(`FPS: ${fps}\nRender Time: ${renderTime}ms`);
});
```

#### Using Color Status Lights

Implement color-coded indicators to reflect performance status:

- **Green**: Good performance
- **Yellow**: Moderate performance
- **Red**: Poor performance

```javascript
const statusLight = this.add.graphics();
statusLight.fillStyle(0x00ff00); // Green
statusLight.fillRect(10, 50, 20, 20);

// Update status based on FPS
if (fps < 30) {
  statusLight.fillStyle(0xff0000); // Red
} else if (fps < 50) {
  statusLight.fillStyle(0xffff00); // Yellow
} else {
  statusLight.fillStyle(0x00ff00); // Green
}
statusLight.fillRect(10, 50, 20, 20);
```

## Best Practices and Error Prevention

1. **Avoid Texture Upload Competition**: Ensure that texture uploads are managed by the loader's internal queue by using `load.image` or `load.spritesheet` instead of `textures.addImage`.

2. **Proper Frame Metadata**: Always provide `frameWidth`, `frameHeight`, and `endFrame` when using `load.spritesheet` to prevent missing frame metadata.

3. **Prevent Recursion in Animations**: When creating animations, ensure that the `frames` field is an array of numbers, not a single number, to avoid errors.

4. **Prevent Stack Overflow**: In scenarios where animations are switched frequently, wrap the `update()` method in a `try/catch` block and use a `_busy` flag to prevent re-entry, avoiding `Maximum call stack size exceeded` errors.

5. **Avoid Naming Conflicts**: Use descriptive suffixes for method names to prevent accidental recursion and infinite loops, such as `_registerAtlasAnims`.

## Conclusion

By implementing these optimization techniques, developers can significantly enhance the performance and visual quality of Phaser 3-based 2D games. Proper management of spritesheets, object pooling, container batching, off-screen culling, and custom rendering, coupled with real-time performance monitoring, ensures a smooth and efficient gaming experience.