# FastAPI 全栈架构

## 说明
使用 FastAPI 构建一个完整的 RESTful API 服务，包括以下关键组件：
- **路由定义**：使用 `@app.get` 和 `@app.post` 等装饰器定义 API 端点。
- **依赖注入**：通过 `Depends` 管理数据库连接和其他依赖项。
- **异步处理**：利用 `async def` 函数实现高效的异步处理。
- **中间件**：添加自定义中间件以处理日志记录、错误处理等。

## 关键代码片段
```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
```

## 常见错误及避免方法
- **依赖注入错误**：确保 `Depends` 中引用的函数正确返回依赖项。
- **异步处理阻塞**：避免在异步函数中使用阻塞操作，使用 `await` 调用异步库函数。
- **中间件错误**：确保中间件函数正确返回响应对象，避免中断请求处理流程。