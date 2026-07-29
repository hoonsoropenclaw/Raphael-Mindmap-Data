# Config File Setup

## 說明...
此技能涉及建立一個配置文件，定義應用程序所需的常數，如目錄路徑、OAuth scopes、Google API 端點等。

## 關鍵代碼片段或模式
```javascript
// Example of defining constants and paths
const CWDIR = process.cwd();
function j(...p: string[]): string {
  return p.join(path.sep);
}
export const SDIR = j(CWDIR, 'secrets');
export const LDIR = j(CWDIR, 'logs');
```

## 常見錯誤及避免方法
- **錯誤**：路徑拼接錯誤，導致文件無法正確訪問。
  **解決方法**：使用 `path.join` 或自定義的 `j` 函數來處理跨平台路徑拼接。
- **錯誤**：敏感信息未正確處理，可能導致安全漏洞。
  **解決方法**：確保敏感文件（如 OAuth 憑證）具有適當的權限設置（例如，模式 600）。