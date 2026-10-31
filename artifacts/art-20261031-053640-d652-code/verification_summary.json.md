# verification_summary.json — 2026-10-31 實測收斂（第二輪修補後最終版）

> 本檔的每個數字都是**機器回算**的，不手抄。產生方式見下方 `reproduce`。
> 第二輪（評審後修補）的重點：把「檢查打在別的行程上」這個假綠燈修掉，
> 全部數字都是重新實跑後回算的。

```json
{
  "generated_at": "2026-10-31T05:35:09+08:00",
  "entrypoint": "bash scripts/run_all.sh",
  "unit_tests": {
    "cmd": "npx vitest run",
    "exit_code": 0,
    "test_files_passed": 6,
    "test_files_total": 6,
    "tests_passed": 82,
    "tests_total": 82,
    "duration_s": 2.12
  },
  "authz_probe": {
    "cmd": "bash scripts/probe_authz.sh",
    "exit_code": 0,
    "total": 34,
    "consistent_count": 34,
    "inconsistent_count": 0,
    "all_consistent": true
  },
  "gate_claim_binding": {
    "cmd": "python3 gates/gate_claim_binding.py --plan <plan.json> --cards fixtures/cards.json --projects fixtures/projects.json",
    "exit_code": 0,
    "ok": true,
    "issues": 0,
    "checks": {
      "frontier_novelty_binding": 0,
      "scenario_not_repeated": true,
      "declared_counts_recomputable": true
    }
  },
  "e2e": {
    "cmd": "npx playwright test",
    "exit_code": 0,
    "passed": 6,
    "duration_s": 6.2,
    "specs": [
      "approval-flow.spec.ts: employee can submit, cannot see approve buttons or delete",
      "approval-flow.spec.ts: principal can approve the principal node",
      "approval-flow.spec.ts: manager can approve the manager node; subsequent approve button hides",
      "persistence.spec.ts: manager-approval survives a page reload (Day-3 acceptance)",
      "persistence.spec.ts: node-2 approval is visible to the principal on a fresh load (shared state)",
      "persistence.spec.ts: opening the page must not overwrite server-side data (adversarial)"
    ]
  },
  "external_threshold": {
    "cmd": "python3 gates/gate_external_threshold.py --thresholds fixtures/thresholds.json --checker-output ...",
    "exit_code": 0,
    "ok": true,
    "threshold_file": "fixtures/thresholds.json",
    "subjects": 2,
    "passed": 2,
    "failed": 0,
    "errors": 0,
    "self_claim_divergences": 0
  },
  "delivery_gate": {
    "overall": "PASS",
    "exit_code": 0,
    "rule": "任一支檢查 exit≠0 → 整體 exit≠0（交付被擋住）"
  }
}
```

## 第二輪修掉的三個「接線沒接起來」bug（只有真的跑整套流程才會現形）

| # | 缺陷 | 症狀 | 修法 | 驗證 |
|---|------|------|------|------|
| 1 | `run_all.sh` 埠號守衛缺失 | 埠 8000 被占用 → uvicorn 綁埠失敗退出 → 腳本仍 curl /health 拿到 200 → **所有檢查打在別的行程上** | 啟動前確認埠是空的；被占用 → exit 2，不沿用既有服務。預設埠 8000→8010、4173→4180 | 埠號守衛生效後 e2e 由「2 failed」變 6/6 通過 |
| 2 | 探針缺 metric 欄位 | 門檻檔宣告 `inconsistent_count`，探針只輸出 `consistent_count` → 外部裁決 `status=error` exit 2 | 兩個欄位都輸出 | 外部裁決 authz_probe → `status=pass` |
| 3 | `BASE` 未 export | `NameError: name 'BASE' is not defined` → 探針輸出空 → 外部裁決 rc=2 | `export BASE` + python 端 `os.environ["BASE"]` | 探針輸出 34 案例全部解析成功 |

## 連帶修掉的三個 harness 層根因

| # | 檔案 | 根因 | 修法 | 回歸驗證 |
|---|------|------|------|----------|
| 1 | `harness/knowledge.py` | `check_novelty` 只用 bigram Jaccard，**Jaccard 懲罰長度差異** → 課綱短語 vs 卡片長標題假陰性 | 加 `containment` + `token_containment`，分數改 `max(jaccard, c×0.85, tk×0.9)` | 87 張卡自我檢查 0 回歸；負向測試仍為 novel |
| 2 | `harness/runs.py` | `practice.scenario_hint` 無條件取 `scenarios[0]`，不查歷史 | `_pick_scenario()` 跳過與已完成專案重疊 ≥0.34 的場景 | dev-web-platform 的場景回 None + 說明「不應重做」 |
| 3 | `gates/gate_claim_binding.py` | ——（這是機制本身） | —— | issues 4 → 0 |

## reproduce

```bash
cd workspace/practice-20261031-perm-scope
bash scripts/run_all.sh          # 全部檢查 + 總裁決，exit 0 = 交付閘門通過
```

逐支輸出：`/tmp/run_all_{vitest,probe,claim,e2e,verdict,backend}.*`

## 已知未修（明文揭露）

- **Windows 未實測**：README 的 Windows 段落是依 Unix 實測結果推導。
- **SQLite 併發寫入未實測**：busy_timeout 有設，但沒有併發壓力測試；定位為單使用者示範。
- **X-Demo-Role / X-Demo-User-Id 是示範機制，不是認證**（標頭可被偽造）。
