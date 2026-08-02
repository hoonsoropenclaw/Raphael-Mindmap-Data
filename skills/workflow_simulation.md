# Workflow Simulation

## 說明...
此技能涉及模擬工作流的執行過程，包括節點狀態的動態更新和日誌的實時記錄。

## 關鍵代碼片段或模式
```javascript
async function runNode(id, input) {
    if (visited.has(id)) return;
    visited.add(id);
    const node = nodeMap[id];
    if (!node) return;

    setNodeStatus(id, 'running');
    log({ ts: Date.now(), level: 'info', nodeId: id, msg: '▶ 開始執行 ' + (node.data.label || node.type) });

    // 模擬延遲
    const dur = variantDurations[node.data.variant] != null ? variantDurations[node.data.variant] : 400;
    await new Promise(r => setTimeout(r, dur));

    // 模擬結果
    const failed = someCondition;
    if (failed) {
        setNodeStatus(id, 'failed', { error: '模擬失敗', durationMs: ms });
        log({ ts: Date.now(), level: 'err', nodeId: id, msg: '✕ 失敗 ' + node.data.label + ' after ' + ms + 'ms' });
        return;
    }
    setNodeStatus(id, 'success', { durationMs: ms });
    log({ ts: Date.now(), level: 'ok', nodeId: id, msg: '✓ ' + (node.data.label || node.type) + ' 完成 (' + ms + 'ms)' });
}
```

## 常見錯誤及避免方法
- **錯誤**：日誌時間戳不正確。
  **解決方法**：確保在調用 `log` 函數時傳遞正確的 `ts` 值，例如使用 `Date.now()` 或 `new Date().toISOString()`。
- **錯誤**：節點狀態更新不同步。
  **解決方法**：使用狀態管理工具（如 Redux 或 React Context）來管理節點狀態，確保所有狀態更新都是同步的。