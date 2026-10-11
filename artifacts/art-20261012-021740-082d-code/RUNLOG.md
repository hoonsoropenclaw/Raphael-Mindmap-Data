# RUNLOG — meeting_pipeline.py (Day 1)

## 測試環境
- 機器：Linux 6.8.0-136-generic（N100 dev 軌環境）
- Python：3.x（pip 已裝 pydub）
- 測試時間：2026-10-11

## 測試輸入
- `/tmp/test_meeting.wav`：5 秒靜音 WAV（160044 bytes，16kHz mono），由 `python -c "wave..."` 產生
- 預期輸出：trace DB 一筆 status='transcribed'，transcript.txt 寫入 dry-run mock 內容

## 執行指令
```bash
# 1. 確認 CLI 參數解析
python meeting_pipeline.py --help
# → 顯示 run 子命令、--db/--work-dir/--dry-run 旗標

# 2. 第一次 dry-run
python meeting_pipeline.py /tmp/test_meeting.wav --dry-run \
  --db /tmp/test_trace.db --work-dir /tmp/mp-work run
# → [stage1] 切成 1 段（24MB/段）
# → [stage2] 轉錄中…（dry_run=True）
# → [完成] transcript: /tmp/mp-work/262d1f34f300/transcript.txt

# 3. 第二次 dry-run（驗證 idempotency 邏輯）
python meeting_pipeline.py /tmp/test_meeting.wav --dry-run \
  --db /tmp/test_trace.db --work-dir /tmp/mp-work run
# → 警告：找到歷史記錄 status=transcribed，繼續處理（idempotency）
# → 預期行為：Day 1 故意繼續處理（status=calendared 才完全跳過）

# 4. 確認 trace DB 寫入
python -c "import sqlite3; c=sqlite3.connect('/tmp/test_trace.db'); \
  print(c.execute('SELECT audio_hash, status, transcript_path FROM traces').fetchall())"
# → [('262d1f34f300...', 'transcribed', '/tmp/mp-work/262d1f34f300/transcript.txt')]
```

## 驗證結果
| 檢查 | 結果 |
|---|---|
| CLI 參數解析 | ✅ |
| trace DB 自動建立 | ✅ |
| Stage 1 pydub 切檔（< 25MB 跳過切） | ✅（5 秒音 < 24MB 不切） |
| Stage 2 dry-run mock | ✅ |
| Stage 2 真實 API 缺金鑰 raise | ✅（已用 SystemExit 提示用 --dry-run） |
| Idempotency: 重複運行偵測到歷史 | ✅（警告訊息正確） |
| 完整 calendared → 跳過 | ⏳（Day 2 才有 stage 3/4，能達到 calendared） |

## 已知限制（Day 1 範圍）
- Stage 3（Gemini 萃取決議）、Stage 4（Google Calendar 建事件）尚未實作
- 切段時粗略用 bytes_per_ms 估算，未做精確 AAC/MP3 時間軸對齊
- 失敗重試未實作
- 沒有 CLI 日誌等級控制（目前都是 print）

## Day 2 待辦
- [ ] Stage 3: Gemini response_schema 萃取 decisions[]
- [ ] Stage 4: Google Calendar events.insert + attendees[]（負責人 email）
- [ ] 完成後狀態 = calendared，第二次運行會完全跳過
- [ ] 增加 --retry 旗標

已重跑驗證：2026-10-11 hermes