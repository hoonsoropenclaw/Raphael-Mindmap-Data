# SQLite Thread Safety

## 說明
配置 SQLite 連接以確保在多線程環境下的線程安全，通過設置 `check_same_thread=False` 並使用鎖機制來序列化寫入操作。

## 關鍵代碼片段
```python
import sqlite3
import threading

class Index:
    def __init__(self, db_path: str):
        self._lock = threading.RLock()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def upsert(self, doc: ExtractedDoc, cls: Classification):
        with self._lock:
            self.conn.execute("INSERT INTO ...")
            self.conn.commit()
```

## 常見錯誤及避免方法
- **錯誤**: 多線程環境下 SQLite 連接競爭導致數據損壞。
  **解決方法**: 使用 `check_same_thread=False` 並結合鎖機制（如 `RLock`）來序列化對數據庫的寫入操作。