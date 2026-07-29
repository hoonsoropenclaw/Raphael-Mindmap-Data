# Rate Limit Logic Testing

## 說明...
### 目的
驗證 API 的 rate limit 機制是否有效，確保在請求超過限制時正確觸發限制。

### 關鍵代碼片段或模式
- **單元測試**:
  ```python
  def test_rate_limit_logic_unit(self):
      from framework.vulnerable_app import _check_rate_limit, RATE_LIMIT_MAX, RATE_LIMIT_BUCKET
      ip = "9.9.9.9"
      RATE_LIMIT_BUCKET.pop(ip, None)
      for i in range(RATE_LIMIT_MAX):
          assert _check_rate_limit(ip), f"failed at i={i}"
      assert _check_rate_limit(ip) is False
      RATE_LIMIT_BUCKET.pop(ip, None)
  ```

### 常見錯誤及避免方法
- **環境變量設置錯誤**: 確保 rate limit 的參數設置正確，避免因參數錯誤導致測試結果不準確。
- **測試數據污染**: 每次測試前清理 rate limit 的狀態，避免測試數據污染導致測試結果不準確。