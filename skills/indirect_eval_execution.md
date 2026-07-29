# Indirect Eval Execution

## 說明...
在編譯後的代碼中，為了讓解構變量（如 `ReactFlow`）在全局作用域中可見，需要使用間接 eval（即 `(0, eval)(compiledString)`）來執行代碼。這樣可以確保變量在全局作用域中可用。

## 關鍵代碼片段或模式
```javascript
const indirectEval = eval;
indirectEval(compiled);
```