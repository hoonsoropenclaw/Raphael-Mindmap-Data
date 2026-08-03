# Micro-Skill: Media and Data Management

## Overview
The `media_and_data_management` micro-skill is designed to handle media files, extract data, and ensure the accuracy and reliability of information systems through meticulous data cleaning and management. This encompasses real-time media processing, asynchronous communication, secure web scraping, data deduplication, normalization, and adherence to Standard Operating Procedures (SOPs).

---

## 1. Real-Time Media Processing and Data Extraction

### 1.1 Real-Time Speech-to-Text Integration

#### 1.1.1 Overview
Utilize the OpenAI Whisper API to perform real-time speech-to-text processing, manage audio streams, handle API requests, and parse transcription results.

#### 1.1.2 Key Features and Implementation

- **Whisper API Integration for File Transcription**
  ```python
  import openai

  def transcribe_audio(file_path: str, api_key: str) -> str:
      with open(file_path, 'rb') as audio_file:
          response = openai.Audio.transcribe("whisper-1", audio_file, api_key=api_key)
      return response.text
  ```

- **Real-Time Speech-to-Text Processing**
  ```python
  import openai
  import io

  def real_time_transcribe(audio_stream: io.BytesIO, api_key: str) -> str:
      response = openai.Audio.transcribe("whisper-1", audio_stream, api_key=api_key)
      return response.text
  ```

- **Media Data Handling**
  ```python
  def validate_audio_format(file_path: str) -> bool:
      supported_formats = ('.wav', '.mp3', '.m4a')
      return file_path.lower().endswith(supported_formats)
  ```

#### 1.1.3 Error Prevention and Handling
Implement robust error handling to manage common issues such as API request failures, timeouts, and unsupported audio formats.

- **Common Errors and Solutions**
  - **API Request Failure or Timeout**: Verify API key correctness, ensure stable network connection, and implement a retry mechanism for temporary errors.
  - **Unsupported Audio File Format**: Confirm audio format compatibility (e.g., WAV, MP3, M4A) and validate before API calls.

- **Key Code Snippet for Error Handling**
  ```python
  def transcribe_audio_with_error_handling(file_path: str, api_key: str) -> str:
      if not validate_audio_format(file_path):
          raise ValueError("Unsupported audio file format.")
      
      try:
          with open(file_path, 'rb') as audio_file:
              response = openai.Audio.transcribe("whisper-1", audio_file, api_key=api_key)
          return response.text
      except openai.error.APIError as e:
          raise Exception(f"API Error: {e}")
      except openai.error.APIConnectionError as e:
          raise Exception(f"Connection Error: {e}")
      except Exception as e:
          raise Exception(f"An error occurred: {e}")
  ```

#### 1.1.4 Best Practices
1. **Secure API Key Management**: Use environment variables or secure storage solutions to manage API keys, avoiding hardcoding.
2. **Efficient Resource Management**: Handle audio streams and files efficiently to prevent memory leaks, especially with large files or real-time streams.
3. **Scalability Considerations**: For high-throughput transcription, implement asynchronous processing or leverage cloud-based solutions.
4. **Continuous Monitoring and Logging**: Implement logging to monitor transcription requests and responses for debugging and performance tuning.

### 1.2 Asynchronous HTTP Communication with `httpx.AsyncClient`

#### 1.2.1 Overview
Perform asynchronous HTTP requests using `httpx.AsyncClient` and implement a robust retry mechanism to handle transient errors.

#### 1.2.2 Asynchronous HTTP Requests with `httpx.AsyncClient`
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get('https://example.com')
    print(response.status_code)
    print(response.text)
```

#### 1.2.3 Implementing a Retry Mechanism with `tenacity`
```python
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
import httpx

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(httpx.RequestError)
)
async def fetch_with_retry(client: httpx.AsyncClient, url: str):
    response = await client.get(url)
    response.raise_for_status()
    return response.text
```

#### 1.2.4 Advanced `asyncio` Features
Utilize advanced `asyncio` features such as task scheduling and event loops to handle multiple HTTP requests concurrently without blocking the main thread.

```python
import asyncio
import httpx

async def fetch_url(client: httpx.AsyncClient, url: str):
    response = await client.get(url)
    response.raise_for_status()
    return response.text

async def main():
    async with httpx.AsyncClient() as client:
        urls = ['https://example.com', 'https://httpbin.org/get']
        tasks = [fetch_url(client, url) for url in urls]
        results = await asyncio.gather(*tasks)
        for content in results:
            print(content)

asyncio.run(main())
```

#### 1.2.5 Common Errors and Prevention
- **HTTP Request Failures**: Verify URL correctness and accessibility, ensure stable network connection, and implement retry mechanisms for transient errors.
- **Resource Contention Leading to Request Failures**: Reuse the `httpx.AsyncClient` instance throughout the application's lifecycle and use asynchronous context managers to manage the client lifecycle.

### 1.3 Asynchronous Media and Speech Processing

#### 1.3.1 Frontend Audio and Video Capture with Asyncio
- **Features**: Securely request and manage user permissions, capture audio and video data in real-time, and stream captured media to the backend via WebSocket for real-time processing.
- **Implementation**
  ```javascript
  // Asynchronous media capture and transmission
  async function captureMedia() {
      try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
          const mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm;codecs=opus' });
          mediaRecorder.start(1000); // Record in 1-second chunks

          const socket = new WebSocket('wss://your-backend-server.com/media-stream');

          socket.onopen = () => {
              console.log('WebSocket connection established');
          };

          mediaRecorder.ondataavailable = async (event) => {
              if (event.data.size > 0) {
                  socket.send(event.data);
              }
          };

          mediaRecorder.onerror = (error) => {
              console.error('MediaRecorder error:', error);
          };

          socket.onerror = (error) => {
              console.error('WebSocket error:', error);
          };
      } catch (error) {
          console.error('Media access denied or unavailable:', error);
      }
  }

  captureMedia();
  ```

- **Error Prevention**: Handle cases where the user denies media access and implement robust error handling for WebSocket connections.

---

## 2. Data Cleaning and Information Management

### 2.1 Data Cleaning with Class Tokens
- **Purpose**: Leverage HTML class tokens to clean and convert data types, such as transforming star ratings from class names into numerical values.
- **Implementation**
  ```python
  from bs4 import BeautifulSoup
  from spider import DataCleaner, FieldSpec

  soup = BeautifulSoup('<p class="star-rating Three"></p>', 'html.parser')
  cleaner = DataCleaner([
      FieldSpec('rating', '.star-rating', type='rating', class_token_index=1)
  ])
  result = cleaner.clean_one(soup, 'u', 't')
  print(result.data['rating'])  # Output: 3
  ```

- **Common Errors and Prevention**: Ensure selectors precisely match HTML class names and incorporate default values or error handling for missing tokens.

### 2.2 URL Deduplication and Normalization
- **URL Normalization**: Standardize URLs to eliminate redundancies by removing fragments, sorting query parameters, and converting URLs to lowercase.
  ```python
  from urllib.parse import urlparse, urlunparse

  def normalize_url(url: str) -> str:
      parsed = urlparse(url)
      normalized = parsed._replace(fragment='')
      if parsed.query:
          query_params = sorted(parsed.query.split('&'))
          normalized = normalized._replace(query='&'.join(query_params))
      return urlunparse(normalized).lower()
  ```

- **URL Deduplication**: Ensure each URL is processed only once using a `Set` or a hash map for large datasets.
  ```python
  from typing import Set

  class Deduper:
      def __init__(self):
          self.seen: Set[str] = set()

      def add(self, url: str) -> bool:
          normalized = normalize_url(url)
          if normalized in self.seen:
              return False
          self.seen.add(normalized)
          return True
  ```

### 2.3 Handling Asynchronous and Multi-threaded Environments
- **Thread Safety**: Use thread locks to prevent race conditions in multi-threaded or asynchronous contexts.
  ```python
  import asyncio
  from asyncio.locks import Lock

  class Deduper:
      def __init__(self):
          self.seen: Set[str] = set()
          self.lock: Lock = asyncio.Lock()

      async def add(self, url: str) -> bool:
          normalized = normalize_url(url)
          async