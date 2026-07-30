# SQLite Integration and Deployment with Docker

## SQLite 存储关闭处理

### 说明
在多线程环境下，确保 SQLite 存储在所有操作完成后正确关闭，以避免连接泄漏或数据损坏。

### 关键代码片段或模式
```python
def close(self):
    if self._conn:
        self._conn.close()
        self._conn = None

def record_event(self, event):
    if self._conn is None:
        raise RuntimeError("EventStore is closed")
    with self._lock:
        self._conn.execute(...)
```

### 常见错误及避免方法
- **错误**: 在连接关闭后尝试进行操作，导致 `NoneType` 错误。
  **解决方法**: 在每次操作前检查连接是否已关闭，并在关闭后立即将连接引用设为 `None`。
- **错误**: 关闭连接时线程仍在使用连接，导致数据竞争或挂起。
  **解决方法**: 使用锁机制确保在关闭连接时没有其他线程正在使用连接，并在必要时使用 `threading.Condition` 进行同步。

## Full Stack Deployment with Docker

### 概述
本指南提供了使用 Docker 和 FastAPI 部署和管理全栈应用的全面指南。它涵盖了为 FastAPI 设置 Docker 容器、集成异步功能以及使用 React Flow 管理前端组件。

---

### Docker 和 FastAPI 设置

#### 描述
本节重点介绍在 Docker 容器内构建和运行 FastAPI 应用，包括设置带有基本功能的异步 FastAPI 模板。

#### 关键代码片段和模式

##### Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -e .[dev]
COPY . .
ENV APP_ENVIRONMENT=production
ENV APP_DATABASE_URL=sqlite+aiosqlite:////tmp/app.db
USER appuser
CMD ["uvicorn", "fastapi_template.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 常见错误及预防措施
- **错误**: 非 root 用户无法写入应用目录。
  - **解决方案**: 在 `Dockerfile` 中使用 `useradd` 命令创建具有适当权限的用户。

---

### 异步 FastAPI 模板设置

#### 配置
```python
# config.py
from pydantic_settings import BaseSettings, NoDecode
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(default="sqlite+aiosqlite:///./live_smoke.db", env="APP_DATABASE_URL")
    # 添加其他设置

    @field_validator("database_url")
    def validate_database_url(cls, v):
        # URL 规范化逻辑
        return v
```

#### 数据库设置
```python
# db.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(settings.database_url, future=True, pool_pre_ping=True)
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)
```

#### 常见错误及预防措施
- **错误**: 环境变量处理不当导致数据库连接失败。
  - **解决方案**: 使用 `pydantic-settings` 和 `NoDecode` 支持 CSV/JSON 列表环境变量解析。
- **错误**: SQLite WAL 文件锁定问题。
  - **解决方案**: 将 SQLite 数据库文件放置在 Docker 容器内的 `/tmp` 目录中，以避免文件锁定问题。

---

### 其他提示
- **环境变量**: 始终验证和清理环境变量，以防止配置相关的错误。
- **日志记录**: 实现强大的日志记录系统，以监控应用行为并有效排查问题。
- **测试**: 使用 Docker Compose 设置多容器环境，以测试 FastAPI 应用与数据库和其他服务的集成。

---

### 全栈开发管理

#### 描述
本节涵盖了使用 React Flow 集成前端组件，包括节点和边缘定义、事件处理和 CDN 集成。

#### 关键代码片段和模式
```javascript
const nodes = [
  { id: '1', type: 'start', position: { x: 250, y: 5 }, data: { label: 'Start' } },
  // 其他节点
];

const edges = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
  // 其他边缘
];

function onNodesChange(changedNodes) {
  setNodes(changedNodes);
}

function onEdgesChange(changedEdges) {
  setEdges(changedEdges);
}

function onConnect(connection) {
  setEdges((eds) => addEdge(connection, eds));
}
```

#### 常见错误及预防措施
- **错误**: 节点或边缘 ID 冲突导致渲染问题。
  - **解决方案**: 使用唯一的 ID 生成策略，例如 UUID。
- **错误**: 事件处理函数未正确绑定，导致事件未触发。
  - **解决方案**: 确保所有事件处理函数都正确绑定到 React Flow 实例。

---

通过遵循本指南，您可以高效地使用 Docker 和 FastAPI 部署和管理全栈应用，为您的项目奠定一个强大且可扩展的基础。