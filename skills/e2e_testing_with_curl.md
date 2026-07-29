# E2E Testing with cURL

## 說明...
此技能涉及使用 curl 模擬不同用戶角色和權限來測試受保護的路由。

### 關鍵代碼片段或模式
```bash
#!/usr/bin/env bash
# E2E RBAC 驗收腳本: 模擬 6 種角色的所有關鍵路徑
set -u
URL=http://localhost:3457

make_token() {
  local role_json="$1"
  printf 'demo:'
  printf '%s' "$role_json" | base64 -w0
}

# 各角色 token (base64 of demo:<JSON>)
GUEST=$(make_token '{"id":"u-guest","name":"訪客","email":"guest@demo","role":"guest"}')
...

check() {
  local desc="$1" expected="$2" got="$3"
  if [[ "$got" == "$expected" ]]; then
    echo "  ✓ $desc (HTTP $got)"
    PASS=$((PASS+1))
  else
    echo "  ✗ $desc (expected $expected, got $got)"
    FAIL=$((FAIL+1))
  fi
}

# 測試案例
...
```

### 常見錯誤及避免方法
- **錯誤**: 測試腳本中角色 token 生成錯誤，導致權限驗證失敗。
  **解決方法**: 確保 token 生成邏輯正確，並使用工具驗證生成的 token 是否符合預期。
- **錯誤**: 測試案例覆蓋不足，漏掉關鍵權限組合。
  **解決方法**: 設計全面的測試案例，覆蓋所有可能的角色和權限組合。
- **錯誤**: 測試環境配置錯誤，導致測試結果不準確。
  **解決方法**: 確保測試環境與生產環境配置一致，並在測試前進行環境檢查。