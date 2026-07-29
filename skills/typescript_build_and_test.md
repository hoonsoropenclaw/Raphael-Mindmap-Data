# TypeScript Build and Test

## 說明
此技能涉及編譯和測試 TypeScript 代碼，以確保所做的更改不會引入新的錯誤並且應用程序能夠正常運行。

## 關鍵代碼片段或模式
1. 運行 TypeScript 編譯器進行編譯檢查：
   ```bash
   tsc --noEmit
   ```
2. 運行應用程序以進行端到端測試：
   ```bash
   npm start
   ```
3. 使用 curl 進行 API 測試：
   ```bash
   curl -s -c /tmp/_cookies.txt -X POST http://127.0.0.1:3000/api/auth/register \
     -H "content-type: application/json" \
     -d '{"email":"alice@example.com","password":"correcthorse","name":"Alice"}'
   ```

## 常見錯誤及錯誤避免方法
- **錯誤**：編譯錯誤導致編譯失敗。
  **避免方法**：在進行更改後立即運行編譯器，並根據錯誤信息進行修正。
- **錯誤**：應用程序運行時出現運行時錯誤。
  **避免方法**：使用調試工具檢查錯誤來源，並確保所有依賴項正確安裝和配置。
- **錯誤**：API 測試失敗。
  **避免方法**：檢查 API 請求的參數和格式，並確保服務器正在運行並且網絡連接正常。