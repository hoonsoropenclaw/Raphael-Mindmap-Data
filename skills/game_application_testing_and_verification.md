# Game Application Testing and Verification

## Target Skill Name: game_application_testing_and_verification

## Target Summary
This micro-skill encompasses the comprehensive testing and verification of a Phaser 3 game application, including scene initialization, simulator tick verification, player movement validation, and HUD log capture with event flow verification.

---

## 1. Phaser Scene Initialization

### **Description**
Initialize the Phaser 3 game scene, set up the main scene, and ensure it is active.

### **Key Code Snippets and Patterns**
```javascript
await page.wait_for_function("() => window.__game && window.__game.scene && window.__game.scene.keys.Main && window.__game.scene.keys.Main.sys.isActive()", timeout=20000)
```

### **Common Errors and Prevention**
- **Error**: Main scene not activated.
  - **Solution**: Ensure all dependent scenes and systems are correctly loaded and initialized when calling `wait_for_function`.

---

## 2. Simulator Tick Verification

### **Description**
Verify that the simulator is running and check if the tick count is incrementing as expected.

### **Key Code Snippets and Patterns**
```javascript
sim_tick = await page.evaluate("() => window.__game.scene.keys.Main.sim ? window.__game.scene.keys.Main.sim.tick : 0")
if sim_tick < 5:
    print(f"FAIL: sim tick = {sim_tick} (expected ≥ 5)")
    return 3
```

### **Common Errors and Prevention**
- **Error**: Tick count not incrementing as expected.
  - **Solution**: Check if the simulator loop is running correctly, ensuring no blocking or infinite loops are affecting the tick count.

---

## 3. Player Movement Verification

### **Description**
Send movement intents and verify that the player's position changes as expected.

### **Key Code Snippets and Patterns**
```javascript
pos_before = await page.evaluate("() => { const s = window.__game.scene.keys.Main; const p = s.sim.entities.find(e => e.kind === 'player'); return p ? {x: p.x, y: p.y} : null; }")
await page.evaluate("() => { window.__game.scene.keys.Main.bridge.emit({ type: 'intent', intent: 'move', args: {direction: [1, 0], word: 'east'}, raw: 'test:east' }); }")
await page.wait_for_timeout(1200)
pos_after = await page.evaluate("() => { const s = window.__game.scene.keys.Main; const p = s.sim.entities.find(e => e.kind === 'player'); return p ? {x: p.x, y: p.y, hp: p.hp} : null; }")
```

### **Common Errors and Prevention**
- **Error**: Player position does not change.
  - **Solution**: Verify that the movement intent is correctly sent and ensure the simulator loop is processing intents and updating the player's position.

---

## 4. HUD Log Capture and Event Flow Verification

### **Description**
Capture HUD logs and verify that the event flow is proceeding as expected.

### **Key Code Snippets and Patterns**
```javascript
n_events = await page.evaluate("() => window.__game.scene.keys.Main._hudLog.length")
if n_events < 4:
    print(f"FAIL: only {n_events} HUD log lines")
    return 3
```

### **Common Errors and Prevention**
- **Error**: Insufficient number of HUD log lines.
  - **Solution**: Check if events are correctly sent to the HUD and ensure the simulator loop is generating events and updating the HUD logs.

---

## Summary of Best Practices

- **Initialization**: Always ensure that all necessary scenes and systems are fully loaded and active before proceeding with tests.
- **Tick Verification**: Monitor the tick count to ensure the simulator is running smoothly without any interruptions.
- **Movement Validation**: Validate player movements by comparing positions before and after sending movement intents.
- **HUD Log Monitoring**: Continuously capture and analyze HUD logs to verify that events are being processed and logged correctly.
- **Error Prevention**: Regularly check for common errors and implement solutions to prevent them, such as ensuring proper initialization, monitoring simulator loops, and verifying event emissions.

By following these guidelines and utilizing the provided code snippets, you can effectively test and verify the functionality of your Phaser 3 game application.