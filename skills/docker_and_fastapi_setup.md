# Docker and FastAPI Setup

## Overview
This micro-skill covers building and running FastAPI applications using Docker containers and setting up an asynchronous FastAPI template with essential features.

---

## Docker Build and Run

### Description
Use a `Dockerfile` to build a Docker image for your FastAPI application and run the container using Docker.

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

## Async FastAPI Template Setup

### Description
Create a FastAPI template that includes asynchronous SQLAlchemy, SQLite/PostgreSQL support, CRUD architecture, OpenAPI documentation, and Prometheus metrics.

### Key Code Snippets and Patterns

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

By following this guide, you can efficiently set up a Dockerized FastAPI application with asynchronous capabilities and essential features, ensuring a robust and scalable foundation for your projects.