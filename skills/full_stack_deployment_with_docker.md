# Full Stack Deployment with Docker

## Overview
This micro-skill provides a comprehensive guide to deploying and managing full-stack applications using Docker and FastAPI. It covers setting up Docker containers for FastAPI, integrating asynchronous features, and managing frontend components with React Flow.

---

## Docker and FastAPI Setup

### Description
This section focuses on building and running FastAPI applications within Docker containers, including setting up an asynchronous FastAPI template with essential features.

### Key Code Snippets and Patterns

#### Dockerfile
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

### Common Errors and Prevention

- **Error**: Non-root users cannot write to the application directory.
  - **Solution**: Use the `useradd` command in the `Dockerfile` to create a user with appropriate permissions.

---

### Async FastAPI Template Setup

#### Configuration
```python
# config.py
from pydantic_settings import BaseSettings, NoDecode
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(default="sqlite+aiosqlite:///./live_smoke.db", env="APP_DATABASE_URL")
    # Add other settings here

    @field_validator("database_url")
    def validate_database_url(cls, v):
        # URL normalization logic
        return v
```

#### Database Setup
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

### Common Errors and Prevention

- **Error**: Improper handling of environment variables leading to database connection failures.
  - **Solution**: Use `pydantic-settings` with `NoDecode` to support CSV/JSON list environment variable parsing.

- **Error**: SQLite WAL file locking issues.
  - **Solution**: Place the SQLite database file in the `/tmp` directory within the Docker container to avoid file locking problems.

---

## Additional Tips

- **Environment Variables**: Always validate and sanitize environment variables to prevent configuration-related errors.
- **Logging**: Implement robust logging to monitor application behavior and troubleshoot issues effectively.
- **Testing**: Use Docker Compose to set up a multi-container environment for testing your FastAPI application alongside databases and other services.

---

## Full Stack Development Management

### Description
This section covers the integration of frontend components using React Flow, including node and edge definitions, event handling, and CDN integration.

### Key Code Snippets and Patterns
```javascript
const nodes = [
  { id: '1', type: 'start', position: { x: 250, y: 5 }, data: { label: 'Start' } },
  // Other nodes
];

const edges = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
  // Other edges
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

### Common Errors and Prevention

- **Error**: Node or edge ID conflicts causing rendering issues.
  - **Solution**: Use a unique ID generation strategy, such as UUID.

- **Error**: Event handler functions not properly bound, leading to non-triggering events.
  - **Solution**: Ensure all event handler functions are correctly bound to the React Flow instance.

---

By following this guide, you can efficiently deploy and manage full-stack applications using Docker and FastAPI, ensuring a robust and scalable foundation for your projects.