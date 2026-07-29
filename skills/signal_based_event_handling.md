# Signal Based Event Handling

## 說明...
使用信號（signals）來處理事件，包括：
- **scan_progress**：在 OCR 掃描過程中發送進度更新。
- **scan_completed**：當 OCR 掃描完成時發送結果。
- **scan_failed**：當 OCR 掃描失敗時發送錯誤訊息。

## 關鍵程式碼片段或模式
```gdscript
signal scan_progress(value: float, phase: String)
signal scan_completed(text: String, confidence: float)
signal scan_failed(message: String)

func _ready() -> void:
    ocr.scan_progress.connect(_on_scan_progress)
    ocr.scan_completed.connect(_on_scan_completed)
    ocr.scan_failed.connect(_on_scan_failed)

func _on_scan_progress(value: float, phase: String) -> void:
    # 更新 UI 進度條
    progress_bar.value = value * 100
    status_label.text = phase

func _on_scan_completed(text: String, confidence: float) -> void:
    result_label.text = text
    status_label.text = "OCR COMPLETED"
```

## 常見錯誤及避免方法
- **錯誤**：信號連接錯誤，導致事件無法觸發。
  **解決方法**：確認信號名稱和連接方法正確，並使用 Godot 的內建信號檢查工具進行驗證。
- **錯誤**：事件處理函數中未正確處理數據，導致 UI 更新失敗。
  **解決方法**：在事件處理函數中檢查接收到的數據類型，並使用 debug 模式進行測試。