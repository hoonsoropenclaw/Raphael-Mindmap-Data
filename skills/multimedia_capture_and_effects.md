# Multimedia Capture and Effects

## Overview
This micro-skill focuses on two key areas:
1. **Video Capture**: Utilizing the `MediaRecorder` API to record gameplay footage from the HTML5 canvas.
2. **2D Visual Effects**: Implementing dynamic visual effects in the Godot game engine to enhance the visual appeal of 2D games.

---

## 1. MediaRecorder Video Capture

### Purpose
Capture and record gameplay footage by leveraging the `canvas.captureStream()` and `MediaRecorder` APIs. This allows developers to create video recordings of their games for promotional, archival, or user-generated content purposes.

### Key Steps and Code Snippet
1. **Capture the Canvas Stream**:
   ```javascript
   const stream = canvas.captureStream();
   ```
   - The `captureStream()` method converts the canvas content into a real-time stream that can be recorded.

2. **Initialize the MediaRecorder**:
   ```javascript
   const recorder = new MediaRecorder(stream);
   const chunks = [];
   ```
   - The `MediaRecorder` object handles the recording process.
   - The `chunks` array stores the recorded data chunks.

3. **Handle Data Availability and Stop Events**:
   ```javascript
   recorder.ondataavailable = (e) => chunks.push(e.data);
   recorder.onstop = () => {
     const blob = new Blob(chunks, { type: 'video/webm' });
     const url = URL.createObjectURL(blob);
     const a = document.createElement('a');
     a.href = url;
     a.download = 'game-recording.webm';
     a.click();
   };
   ```
   - `ondataavailable` collects the recorded data.
   - `onstop` processes the collected data into a downloadable video file.

4. **Start and Stop Recording**:
   ```javascript
   recorder.start();
   // Stop recording after a certain condition or event
   recorder.stop();
   ```
   - `start()` begins the recording process.
   - `stop()` ends the recording and triggers the `onstop` event.

### Common Errors and Prevention
- **Error**: The recorded video does not play.
  - **Solution**: Ensure the MIME type passed to the `Blob` constructor matches the format used by `MediaRecorder`. For example, use `'video/webm'`.
    ```javascript
    const blob = new Blob(chunks, { type: 'video/webm' });
    ```
- **Error**: Performance issues during recording.
  - **Solution**: Optimize the canvas rendering performance by reducing the complexity of visual elements or lowering the frame rate of the recording.
    ```javascript
    const recorder = new MediaRecorder(stream, { videoBitsPerSecond: 2500000 });
    ```
    - Adjusting `videoBitsPerSecond` can help balance quality and performance.

---

## 2. Godot 2D Visual Effects

### Purpose
Enhance the visual quality of 2D games by implementing dynamic effects such as particles, dynamic lighting, and post-processing effects using Godot's built-in tools and scripting capabilities.

### Key Components and Code Snippets

#### 1. Particle Systems
- **Overview**: Create realistic effects like fire, smoke, and explosions using `GpuParticles2D` and `CPUParticles2D`.
- **Example Code**:
  ```gdscript
  extends Node2D
  class_name Emitter

  @export var particle_type: String = "fire"
  @export var rate: int = 14
  @export var lifetime_ms: float = 1200.0
  @export var initial_speed: float = 280.0
  @export var spread_deg: float = 40.0
  @export var size: float = 10.0
  @export var color_h: float = 0.05
  @export var color_s: float = 1.0
  @export var color_v: float = 1.0

  @onready var particles: GpuParticles2D = $Particles
  var rng := RandomNumberGenerator.new()
  var is_emitting := false

  func _ready() -> void:
      rng.randomize()
      _apply_particle_process_material()

  func _apply_particle_process_material() -> void:
      var pm := ParticleProcessMaterial.new()
      pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_POINT
      pm.direction = Vector3(0, -1, 0)
      pm.spread = spread_deg
      pm.initial_velocity_min = initial_speed * 0.6
      pm.initial_velocity_max = initial_speed * 1.2
      pm.gravity = Vector3(0, 980, 0)
      pm.scale_min = size * 0.4
      pm.scale_max = size * 0.7
      pm.color = Color.from_hsv(color_h, color_s, color_v)
      pm.damping_min = 0.5
      pm.damping_max = 1.5
      particles.process_material = pm
  ```
  - **Explanation**: This script sets up a particle emitter with customizable parameters for different effects.

#### 2. Dynamic Lighting
- **Overview**: Use `PointLight2D` and `LightOccluder2D` to simulate dynamic lighting and shadows.
- **Example**:
  - Add a `PointLight2D` node to your scene to act as a light source.
  - Use `LightOccluder2D` nodes to define areas where light is blocked, creating realistic shadow effects.

#### 3. Post-Processing Effects
- **Overview**: Implement effects like motion blur, camera shake, and bloom to enhance the visual experience.
- **Example**:
  - **Motion Blur**: Use Godot's built-in `MotionBlur` effect.
    ```gdscript
    func _ready():
        var motion_blur = get_node("MotionBlur")
        motion_blur.enabled = true
        motion_blur.strength = 0.5
    ```
  - **Camera Shake**: Create a script to randomly offset the camera's position for a shaking effect.
    ```gdscript
    func camera_shake(duration: float, magnitude: float):
        var timer = Timer.new()
        timer.wait_time = duration
        timer.autostart = true
        add_child(timer)
        var original_position = $Camera2D.position
        for i in range(int(duration / 0.01)):
            $Camera2D.position = original_position + Vector2(rng.randf_range(-magnitude, magnitude), rng.randf_range(-magnitude, magnitude))
            yield(get_tree(), "idle_frame")
        $Camera2D.position = original_position
    ```
  - **Bloom**: Enable the `Bloom` effect in the scene's `Environment` settings.

### Best Practices
- **Performance Optimization**: Always test visual effects on target devices to ensure they do not negatively impact performance.
- **Consistency**: Maintain a consistent visual style across all effects to ensure a cohesive look and feel.
- **Modularity**: Create reusable effect components to streamline development and improve maintainability.

---

## Summary
By mastering both video capture using the `MediaRecorder` API and 2D visual effects in Godot, developers can enhance their games with engaging visuals and create high-quality recordings for various purposes. This micro-skill equips you with the tools and knowledge to implement these features effectively and efficiently.