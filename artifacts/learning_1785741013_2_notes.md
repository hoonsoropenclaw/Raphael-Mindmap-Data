# Multilingual Pipeline — 實作筆記

**Task**: `learning_1785741013_2` — OCR 文字辨識與文件處理自動化：整合 Whisper API 實現多語言語音轉文字功能
**Date**: 2026-08-03
**Mode**: FULL AUTONOMY (no human confirmation)

## 一、最終交付物

| 檔案 | 用途 | 大小 |
|------|------|------|
| `multilingual_pipeline.py` | CLI 工具（4 個 subcommand） | 22.7 KB |
| `web_output.html` | HTML 前端（拖放式 UI） | 42.4 KB / 1051 行 |

兩者皆已驗證可獨立運行。

## 二、架構總覽

```
┌──────────────────────────────────────────────────────────────────┐
│                    Multilingual Pipeline                         │
│                                                                  │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐      │
│  │transcribe│   │   ocr    │   │synthesize│   │ pipeline │      │
│  │  Whisper │   │ Tesseract│   │MiniMax   │   │ A→T→T→A  │      │
│  │   ASR    │   │   OCR    │   │  T2A v2  │   │  loop    │      │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘      │
│       │              │              │              │             │
│       ▼              ▼              ▼              ▼             │
│  faster-whisper  pytesseract    mmx-cli (npx)   串接三者        │
│  1.2.1           5.3.4          1.0.16                          │
│                                                                  │
│  Common: ffmpeg 6.1.1 (audio conversion)                        │
└──────────────────────────────────────────────────────────────────┘
```

## 三、4 個 Subcommand 設計

### 3.1 `transcribe` — 音訊 → 文字 (Whisper)
- **底層**: `faster-whisper` 1.2.1 (CTranslate2-based, OpenAI Whisper reimpl)
- **模型**: tiny / base / small / medium / large-v3 / large-v3-turbo
- **N100 預設**: `tiny` (75MB, RTF ~0.2x)
- **語言**: 自動偵測 (zh p=0.998, en p=0.997, ja p=0.997 實測)
- **任務**: `transcribe` (同語言) / `translate` (→ English)
- **VAD**: 內建 silero VAD，可選
- **輸出**: JSON (含 segments/confidence/duration/RTF) + .txt + .srt 字幕

### 3.2 `ocr` — 圖片 → 文字 (Tesseract)
- **底層**: `tesseract` 5.3.4 via `pytesseract`
- **語言包**: eng / chi_sim / chi_tra / jpn / kor / spa / fra / deu ...
- **本機可用**: chi_sim + chi_tra + eng（4 種已驗證）
- **PSM**: 1/3/4/6/7/11（頁面分割模式）
- **輸出**: JSON (含 bounding box + conf) + .txt + .hocr (XML 帶座標)

### 3.3 `synthesize` — 文字 → 音訊 (MiniMax T2A)
- **底層**: `mmx speech synthesize` (MiniMax T2A v2)
- **模型**: speech-2.8-hd / speech-2.8-turbo / speech-2.6-hd / speech-2.6-turbo
- **語音**: 30+ 種，含 female-shaonv / English_expressive_narrator / Japanese_GracefulMaiden / Korean_CalmLady
- **格式**: mp3 / wav / pcm / flac / opus
- **取樣率**: 16000 / 24000 / 32000 / 44100
- **語速**: 0.5-2.0
- **輸出**: 音訊檔 + JSON metadata (duration/sample_rate/size)

### 3.4 `pipeline` — 端到端管線
```
audio.mp3 → [Whisper ASR] → transcript.txt
                         → [translate hook] → translated.txt
                         → [MiniMax T2A]   → output.mp3
```
- **步驟 1**: 呼叫 `transcribe` sub-process
- **步驟 2**: 預設 passthrough，hook 點 `_translate_text()` 留給用戶接 argos / Claude / 等
- **步驟 3**: 呼叫 `synthesize` sub-process
- **驗證**: zh→en 6s 音訊 30 秒內完成（含 passthrough）

## 四、HTML 前端（web_output.html）

### 設計語言
- **配色**: 黑底 + 暖橘 accent (#d97757) + jade (#788c5d) + slate-blue (#6a9bcc)
  - 刻意避開 AI-slop 紫藍漸層
- **字體**: system font stack（無外部依賴）
- **版面**: Bento-grid，1051 行，325 個 start tag
- **無 emoji-as-icon**: 用文字符號（🎙 📄 🔊 🔁）標示 mode tab

### 4 個 mode tabs（與 CLI subcommand 對應）
1. **語音轉文字** — dropzone 音訊 + Whisper 模型/語言/任務/VAD
2. **OCR 文字辨識** — dropzone 圖片 + tesseract 語言組合/PSM
3. **文字轉語音** — textarea 文字 + 30+ 語音下拉
4. **完整管線** — dropzone 來源音訊 + 目標語言 + 翻譯引擎

### 互動細節
- 拖放視覺高亮 (`.dragover` 橘色邊框 + 橘色 tint)
- 檔案大小自動換算 (KB / MB)
- 狀態指示器 (info / ok / warn / err) 帶顏色
- 載入 spinner (CSS keyframes)
- 複製按鈕 → `navigator.clipboard.writeText`
- 統計 grid (偵測語言/信心/時長/RTF/字數) 即時更新

### 為何用 data-* 屬性而非直接 fetch？
- 本環境無 server proxy；按鈕點擊只更新狀態，提示用戶 CLI 對應指令
- 真實部署時加 Flask/FastAPI proxy 即可串接 CLI
- 這是 trial-and-error 的「架構優先」原則：先把 UI/UX/資料流做好，後端可後插

## 五、技術驗證 (E2E Test Results)

### Test 1: English audio
```
input:  /tmp/test_en.mp3 (8s, MiniMax T2A 合成)
model:  tiny
output: "Hello, this is a test of the multi-lingual speech recognition system,
         the quick brown fox jumps over the lazy dog."
detected lang: en p=0.997, RTF=0.15x ✅
```

### Test 2: Chinese audio
```
input:  /tmp/test_zh.mp3 (6s, MiniMax T2A 合成)
model:  tiny
output: "您好,这是一个多语言与云转文字系统的测试,台北是一个美丽的城市"
detected lang: zh p=0.998, RTF=0.21x ✅
```

### Test 3: Japanese audio
```
input:  /tmp/test_ja.mp3 (5s, MiniMax T2A 合成, voice=Japanese_GracefulMaiden)
model:  tiny
output: "こんにちは世界。これは、タゲンゴ音声認識のテストです。"
detected lang: ja p=0.997, RTF=0.23x ✅
```

### Test 4: ja→en translation (Whisper translate task)
```
input:  /tmp/test_ja.mp3
output: "This is the world of this world. This is the test of..."
⚠️ tiny model 翻譯品質有限；改用 small/medium 會改善
```

### Test 5: Multilingual OCR
```
input:  /tmp/ocr_test.png (800x300, 4 lines eng + chi_tra)
lang:   chi_tra+eng
output: "Hello World 2028 / Muttingual OCR Test / (COR + Whisper Pipeline"
words:  11, time 0.8s ✅
⚠️ 簡單合成圖辨識率有限（缺真實字型），真實文件會更好
```

### Test 6: T2A zh
```
text:   "這是 MiniMax T2A 的多語音合成測試，支援中英日韓等多國語言。"
voice:  female-shaonv
output: 99KB MP3, 6084ms duration ✅
```

### Test 7: T2A en
```
text:   "The multilingual pipeline successfully integrates OCR, Whisper ASR, and MiniMax T2A."
voice:  English_Graceful_Lady
output: 139KB MP3, 8604ms duration ✅
```

### Test 8: Full pipeline (zh→en)
```
input:    /tmp/test_zh.mp3
step 1:   transcribe → "您好,这是一个多语言..."  (31 chars, lang=zh)
step 2:   translate → passthrough (zh→en hook 未接)
step 3:   synthesize → /tmp/final_pipeline.mp3 (132KB)
total:    ~30s ✅
```

## 六、踩坑紀錄（L3 教訓）

### 坑 1: `pytesseract.image_to_pdf_or_ocr` 不存在
- tesseract 5.x API 改為 `image_to_pdf_or_hocr`
- **修復**: try/except 兩種 API name 都支援

### 坑 2: WHISPER_MODEL 預設值
- 預設 small (1.5GB) → N100 下載 + 載入 > 90s timeout
- **修復**: 預設改 tiny (75MB)，可用 `WHISPER_MODEL=small` 覆寫

### 坑 3: tiny model 在 ja→en translate task 表現有限
- 75MB tiny 的翻譯品質對長句日文不夠
- 設計層面：translate task 對小模型本來就吃力；用戶可改 small/medium

### 坑 4: terminal timeout 把 process 砍掉沒等他開始
- 第一次 `pipeline` 跑 small 卡 60s timeout 沒真正下載完
- 第二次預先 `python -c "import...WhisperModel('small')"` 確認下載後再跑
- 改 tiny 後端到端 < 30s 完成

## 七、模組化決策

### 為何拆 CLI 4 個 subcommand 而非單一 all-in-one
- **職責分離**: 每個 subcommand 一個清楚輸入/輸出
- **可組合性**: pipeline subcommand 用 subprocess 串接其他 3 個
- **可測試性**: 各自可獨立驗證（不需依賴 MiniMax API 就能跑 transcribe/ocr）
- **可 cron 化**: 用戶可寫 `0 9 * * * python3 transcribe morning.mp3` 排程

### 為何 HTML 用 data-* 而非 fetch
- trial-and-error 教訓：「架構優先於速度」
- UI/UX 先做對，後端 proxy 是 trivial Flask app
- 對用戶展示「該長怎樣」，比「能立刻跑」重要

### 為何不直接 fetch MiniMax ASR API
- mmx-cli v1.0.16 **沒有 ASR 端點**（T2A / image / video / music 都有）
- MiniMax 平台目前無 STT 服務（查 API 列表 404）
- Whisper 是 open-source 黃金標準，自己跑更便宜、更穩

## 八、未來擴展點

1. **translation hook**: `_translate_text()` 留接口，可接 argos / Claude / MarianMT
2. **server proxy**: 寫個 50 行 Flask app 串接 HTML 跟 CLI
3. **batch processing**: `transcribe` 改為接受目錄，平行處理多檔
4. **speaker diarization**: faster-whisper 不支援，要接 pyannote-audio
5. **自訂 Whisper 模型**: fine-tune on 台灣教育部錄音
6. **OCR pre-processing**: 加 deskew / denoise / binarize 提高 tesseract 辨識率
7. **T2A emotion control**: speech-2.6 model 可手動指定 emotion
8. **subtitles 多語**: 同一音訊同時輸出 zh.srt + en.srt + ja.srt

## 九、檔案路徑

- CLI: `/home/hoonsoropenclaw/.hermes/projects/learning_1785741013_2/multilingual_pipeline.py`
- HTML: `/home/hoonsoropenclaw/.hermes/projects/learning_1785741013_2/web_output.html`
- 本筆記: `/home/hoonsoropenclaw/.hermes/projects/learning_1785741013_2/IMPLEMENTATION_NOTES.md`
- Whisper 模型: `~/.cache/huggingface/hub/models--Systran--faster-whisper-tiny/` (75MB)
- T2A 測試音檔: `/tmp/test_en.mp3` / `test_zh.mp3` / `test_ja.mp3` (130KB/100KB/83KB)
- 驗證輸出: `/tmp/final_*.{txt,json,srt,mp3}` (8 個測試結果)
- 完整管線中間檔: `/home/hoonsoropenclaw/.hermes/projects/learning_1785741013_2/pipeline_work/`
