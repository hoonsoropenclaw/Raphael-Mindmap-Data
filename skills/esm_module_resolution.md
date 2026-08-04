# ESM Module Resolution

## 說明...
### 問題描述
在 ESM 環境中，模組解析可能會因為路徑或版本不匹配而導致錯誤。

### 錯誤原因
- 模組路徑錯誤或版本不匹配。
- 某些模組缺少 default export。

### 解決方法
- **步驟 1**：確認 import map 中的路徑與實際模組的路徑一致。
- **步驟 2**：對於沒有 default export 的模組，使用具名 import。
  ```javascript
  import { ReactFlow, Controls, MiniMap } from '@xyflow/react';
  ```
- **步驟 3**：使用瀏覽器開發者工具檢查模組解析路徑，確保沒有錯誤。