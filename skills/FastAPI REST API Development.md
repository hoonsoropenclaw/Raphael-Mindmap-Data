# FastAPI REST API Development

## Overview

### Target Skill Name
FastAPI REST API Development

### Target Summary
Develop high-performance RESTful APIs and WebSocket endpoints using the FastAPI framework, focusing on rapid development, scalability, and efficient error handling.

## Key Components

### 1. RESTful API Endpoint Creation

#### Explanation
Creating RESTful API endpoints in FastAPI involves handling HTTP requests, processing data, and returning appropriate responses with correct HTTP status codes. FastAPI's use of Python type hints and asynchronous programming ensures high performance and ease of use.

#### Key Code Snippets
```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}
```

#### Common Errors and Prevention
- **Error**: Forgetting to import necessary modules or decorators.
  - **Solution**: Always ensure that `FastAPI` and required decorators (e.g., `@app.get`) are imported at the beginning of your script.
- **Error**: Not handling exceptions, resulting in a 500 Internal Server Error.
  - **Solution**: Use `try-except` blocks to catch exceptions and return appropriate HTTP status codes with meaningful error messages.

### 2. Custom Error Handling

#### Explanation
Implementing custom error handling in FastAPI allows for more specific error messages and status codes to be returned, enhancing the API's robustness and user experience.

#### Key Code Snippets
```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"{exc.name} is not a unicorn"},
    )

@app.get("/unicorn/{name}")
async def get_unicorn(name: str):
    if name != "unicorn":
        raise UnicornException(name=name)
    return {"unicorn": name}
```

#### Common Errors and Prevention
- **Error**: Failing to correctly register the exception handler.
  - **Solution**: Use the `@app.exception_handler` decorator to register custom exception handlers.
- **Error**: Not returning a `Response` object in the exception handler.
  - **Solution**: Ensure that the exception handler returns a `Response` object, such as `JSONResponse`, to provide a proper response to the client.

### 3. Serving Static Files

#### Explanation
Serving static files (e.g., HTML, CSS, JS) in FastAPI involves configuring endpoints to return file responses. This is useful for serving frontend applications or static content alongside your API.

#### Key Code Snippets
```python
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()

@app.get("/dashboard", include_in_schema=False)
async def dashboard():
    return FileResponse(Path(__file__).parent.parent / "web_output.html", media_type="text/html")
```

#### Common Errors and Prevention
- **Error**: Incorrect file path, leading to a 404 Not Found error.
  - **Solution**: Use `Path(__file__).parent` to dynamically obtain the current file directory and construct the correct file path.
- **Error**: Not setting the correct `media_type`.
  - **Solution**: Set the appropriate `media_type` based on the file type, such as `text/html` for HTML files, to ensure the browser interprets the file correctly.

### 4. WebSocket Endpoint Management

#### Explanation
FastAPI supports WebSocket connections, enabling real-time bidirectional communication between the client and server. This is useful for applications like chat services, live updates, and real-time data feeds.

#### Key Code Snippets
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
```

#### Common Errors and Prevention
- **Error**: Not properly accepting the WebSocket connection.
  - **Solution**: Always call `await websocket.accept()` before attempting to send or receive data.
- **Error**: Not handling disconnections gracefully.
  - **Solution**: Use try-except blocks to catch `WebSocketDisconnect` exceptions and handle them appropriately.

## Summary

By mastering the creation of RESTful API endpoints, implementing custom error handling, serving static files, and managing WebSocket connections, you can build robust, efficient, and real-time applications using FastAPI. Always ensure that necessary modules and decorators are imported, handle exceptions properly, and configure file and WebSocket responses with accurate paths and media types to prevent common pitfalls.

## Additional Considerations for FastAPI REST API Implementation

### Routing Design and Request Handling

#### Explanation
Proper routing design is crucial for building scalable and maintainable APIs. FastAPI allows for clear and concise routing, making it easy to organize endpoints and handle different HTTP methods.

#### Key Code Snippets
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Event(BaseModel):
    title: str
    start: str
    remind: list

@app.post("/api/events")
def add_event(event: Event):
    # 處理事件創建邏輯
    return {"message": "Event created"}
```

#### Common Errors and Prevention
- **Error**: Routing design not aligned with REST principles, leading to endpoint conflicts.
  - **Solution**: Use clear and consistent naming conventions for routes, such as `/api/events` for event-related operations.
- **Error**: Lack of request validation, causing invalid data to be processed.
  - **Solution**: Utilize Pydantic models to enforce data validation and ensure that incoming requests meet the required schema.

### Serialization and Data Handling

#### Explanation
Serialization is the process of converting complex data types into a format that can be easily transmitted or stored. FastAPI uses Pydantic for data handling and serialization, ensuring that data is correctly formatted and validated.

#### Key Code Snippets
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    email: str

@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    user = {"id": user_id, "name": "John Doe", "email": "john.doe@example.com"}
    return user
```

#### Common Errors and Prevention
- **Error**: Incorrect data types being returned, causing client-side parsing issues.
  - **Solution**: Use Pydantic models to define the expected data structure and ensure that the returned data matches the defined schema.
- **Error**: Not handling nested data structures properly.
  - **Solution**: Utilize nested Pydantic models to handle complex data structures and ensure that all nested fields are correctly validated and serialized.

### Security and Authentication

#### Explanation
Implementing security measures and authentication mechanisms is essential for protecting your API from unauthorized access and potential threats. FastAPI provides built-in support for various security features, including OAuth2, JWT, and more.

#### Key Code Snippets
```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # 處理身份驗證邏輯
    if form_data.username == "john" and form_data.password == "secret":
        return {"access_token": "token", "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

@app.get("/api/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    # 處理受保護的路由邏輯
    return {"message": "You are