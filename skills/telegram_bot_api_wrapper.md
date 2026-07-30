# Telegram Bot API Wrapper

## 說明
此模組封裝了 Telegram Bot 的 `sendMessage` API，並支持 DRY_RUN 模式和 Mock 後端，以便在測試和試錯階段使用。

## 關鍵代碼片段
```python
class SendBackend(Protocol):
    def post(self, url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        ...

class RealBackend:
    def post(self, url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        ...

class DryRunBackend:
    def post(self, url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        ...

class MockBackend:
    def post(self, url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        ...
```

## 常見錯誤及避免方法
- **錯誤**：在 DRY_RUN 模式下未正確處理 API 請求，導致測試結果不準確。
  **避免方法**：在 DRY_RUN 模式下，使用 `DryRunBackend` 類來模擬 API 請求，並將請求內容打印到控制台。
- **錯誤**：在 Mock 後端中未正確收集請求數據，導致測試失敗。
  **避免方法**：在 `MockBackend` 類中，將每次請求的數據存儲到 `self.calls` 列表中，以便後續驗證。