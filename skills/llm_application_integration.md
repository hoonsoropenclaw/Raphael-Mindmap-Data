# LLM Application Integration

## Overview
The **llm_application_integration** micro-skill is designed to empower developers to build comprehensive applications powered by large language models (LLMs). This includes setting up full-stack environments, integrating command-line interfaces (CLI), interacting with RESTful API endpoints, managing databases with FastAPI and SQLAlchemy, and implementing an audio transcription pipeline using the Whisper API. This document consolidates the essential components, code snippets, and best practices to ensure a seamless and efficient integration process.

---

## 1. Full-Stack Development for LLM Applications

### 1.1 LLM API Client Integration

#### 1.1.1 API Key and Base URL Management
- **Loading API Key**: Securely retrieve the API key from environment variables or a configuration file.
  ```python
  def _load_api_key() -> str:
      return os.getenv('MINIMAX_API_KEY') or open('api_key.txt').read().strip()
  ```
- **Loading Base URL**: Fetch the base URL for the LLM API from environment variables or default to a predefined URL.
  ```python
  def _load_base_url() -> str:
      return os.getenv('MINIMAX_API_BASE_URL') or 'https://api.minimax.com'
  ```

#### 1.1.2 API Request Construction
- **Headers**: Configure headers with authorization and content type.
  ```python
  headers = {
      'Authorization': f'Bearer {api_key}',
      'Content-Type': 'application/json'
  }
  ```
- **Payload**: Structure the payload with system and user messages, model selection, and temperature settings.
  ```python
  data = {
      'messages': [
          {'role': 'system', 'content': 'You are a helpful assistant that generates scripts.'},
          {'role': 'user', 'content': f'{ocr_text} / {user_intent}'}
      ],
      'model': 'MiniMax-Text-01',
      'temperature': 0.7
  }
  ```

#### 1.1.3 API Response Handling
- **Sending Requests**: Utilize the `requests` library to send POST requests to the LLM API.
  ```python
  response = requests.post(f'{base_url}/v1/text/chatcompletion_v2', headers=headers, json=data)
  ```
- **Error Handling**: Implement robust error handling to manage network issues, API errors, and unexpected responses.
  ```python
  try:
      response.raise_for_status()
      # Proceed with response processing
  except requests.exceptions.HTTPError as http_err:
      print(f'HTTP error occurred: {http_err}')
  except Exception as err:
      print(f'Other error occurred: {err}')
  ```

#### 1.1.4 Response Parsing
- **Parsing Script Response**: Extract the script from the LLM response using a dedicated parsing function.
  ```python
  return _parse_script_response(response.text, response.json())
  ```

### 1.2 Common Errors and Prevention
- **API Endpoint or Format Assumptions**: Always verify API endpoints and formats using tools like `curl` before making actual requests.
- **Unhandled API Exceptions**: Always check the response status code and handle exceptions to prevent application crashes.

### 1.3 LLM Output Parser

#### 1.3.1 Parsing Logic
- **Language Extraction**: Identify the programming language specified in the LLM output.
  ```python
  language = 'python'
  for line in text.splitlines():
      if line.startswith('# language:'):
          language = line.split(':', 1)[1].strip()
          break
  ```
- **Explanation Extraction**: Extract any explanatory comments provided by the LLM.
  ```python
  explanation = ''
  for line in text.splitlines():
      if line.startswith('# explanation:'):
          explanation = line.split(':', 1)[1].strip()
          break
  ```
- **Script Extraction**: Remove any markdown fencing and extract the core script content.
  ```python
  if '```' in text:
      parts = text.split('```')
      if len(parts) >= 3:
          body = parts[1]
          if '\n' in body:
              body = body.split('\n', 1)[1]
      else:
          body = parts[1]
  else:
      body = text
  ```
- **Removal of Footer Explanations**: Trim any trailing explanation sections or notes.
  ```python
  cut_markers = ['\n### ', '\n## ', '\nNote:', '\n---', '\n**Note', '\n說明：']
  for marker in cut_markers:
      idx = body.find(marker)
      if idx >= 0:
          body = body[:idx]
  ```

#### 1.3.2 Result Structuring
- **ScriptGenResult**: Encapsulate the parsed script, language, explanation, and raw response.
  ```python
  return ScriptGenResult(script=body.strip(), language=language, explanation=explanation, raw=raw)
  ```

### 1.4 Common Errors and Prevention
- **Unstable LLM Output Formats**: Implement fault-tolerant parsing strategies, such as extracting headers first and handling fencing and footer explanations conditionally.
- **Mismatched Fencing Marks**: Ensure that markdown fencing marks are properly paired and handle cases where only the opening fence is present.

### 1.5 Integration and Workflow

#### 1.5.1 CLI Integration
- **Command-Line Interface**: Develop a CLI to accept user inputs, trigger the LLM API, and display or store the generated scripts.
  ```python
  import argparse
  import sys
  from llm_api_client import generate_script
  from llm_output_parser import ScriptGenResult

  def main():
      parser = argparse.ArgumentParser(description='Generate scripts using MiniMax LLM API')
      parser.add_argument('ocr_text', help='OCR text input')
      parser.add_argument('user_intent', help='User intent for script generation')
      args = parser.parse_args()

      script_result = generate_script(args.ocr_text, args.user_intent)
      print(f'Language: {script_result.language}')
      print(f'Explanation: {script_result.explanation}')
      print(f'Script:\n{script_result.script}')

  if __name__ == '__main__':
      main()
  ```

#### 1.5.2 Error Prevention and Logging
- **Logging**: Implement logging to track API requests, responses, and any errors encountered during processing.
  ```python
  import logging

  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger(__name__)

  logger.info('API request sent')
  logger.error(f'API error: {err}')
  ```
- **Validation**: Validate user inputs and API responses to ensure data integrity and prevent malformed requests.

#### 1.5.3 Deployment Considerations
- **Environment Configuration**: Use environment variables or configuration files to manage API keys and endpoints securely.
- **Scalability**: Design the application to handle varying loads and integrate with cloud services if necessary.
- **Security**: Implement security best practices, such as input sanitization and secure storage of API keys.

---

## 2. Configuring FastAPI and SQLAlchemy for Database Management

### 2.1 Purpose
Configure FastAPI to work with SQLAlchemy ORM, including setting up the database engine, session factory, and implementing basic CRUD operations for efficient data management.

### 2.2 Key Components and Code Snippets

#### 2.2.1 Database Engine and Session Factory
- **Purpose**: Establish a connection to the database and manage sessions for database interactions.
- **Code**:
  ```python
  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker

  DATABASE_URL = "postgresql://user:password@localhost:5432/mydatabase"
  CONNECT_ARGS = {"check_same_thread": False}  # Adjust based on database type

  engine = create_engine(DATABASE_URL, connect_args=CONNECT_ARGS)
  SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
  ```

#### 2.2.2 Dependency Injection for Database Sessions
- **Purpose**: Facilitate dependency injection to manage database sessions within FastAPI routes.
- **Code**:
  ```python
  from fastapi import Depends, FastAPI, HTTPException
  from sqlalchemy.orm import Session

  app = FastAPI()

  def get_db():
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()

  @app.get("/items/{item_id}")
  def read_item(item_id: int, db: Session = Depends(get_db)):
      item = db.query(Item).filter(Item.id == item_id).first()
      if item is None:
          raise HTTPException(status_code=404, detail="Item not found")
      return item
  ```

### 2.3 Common Errors and Prevention

#### 2.3.1 Incorrect Database Connection Pool Configuration
- **Issue**: Improper configuration can lead to performance bottlenecks or connection leaks.
- **Solution**: Choose the appropriate connection pool type based on application needs. For example, use `StaticPool` for testing.
  ```python
  engine = create_engine(DATABASE_URL, poolclass=StaticPool, connect_args=CONNECT_ARGS)
  ```

#### 2.3.2 Improper Handling of Session Lifecycle
- **Issue**: Not closing sessions can cause connection leaks.
- **Solution**: Ensure sessions are closed after each request or use dependency injection to manage lifecycle.
  ```python
  def get_db():
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()
  ```

#### 2.3.3 Inadequate Error Handling in Database Operations
- **Issue**: Lack of error handling can expose sensitive