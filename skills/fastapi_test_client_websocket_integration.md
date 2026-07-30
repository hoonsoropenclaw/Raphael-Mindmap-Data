# FastAPI TestClient WebSocket Integration

## 說明
使用 FastAPI 的 `TestClient` 進行 WebSocket 的集成測試，驗證 WebSocket 連接和消息傳遞。

## 關鍵代碼片段
```python
from fastapi.testclient import TestClient
from src.app import app

def test_transcribe_upload_emits_bus_event():
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            # 觸發上傳以生成事件
            client.post(
                "/api/transcribe",
                files={"audio": ("a.mp3", io.BytesIO(b"x" * 500), "audio/mpeg")},
            )
            # 等待 WebSocket 消息
            try:
                msg = ws.receive_json()
            except Exception as e:
                pytest.fail(f"did not receive WS message: {e}")
            assert msg.get("type") == "transcript.completed"
            assert msg["payload"]["backend"] == "mock"
```

## 常見錯誤及避免方法
- **WebSocket 連接未正確建立**：確保在調用 `receive_json()` 之前，WebSocket 連接已經成功建立。
- **消息接收超時**：設置合理的超時時間，並在測試中處理可能的超時異常。