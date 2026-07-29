# AI Application with Computer Vision Integration

## Overview

### Target Skill Name
`ai_application_with_cv_integration`

### Target Summary
Combine computer vision (CV) technologies with AI applications to optimize functionality and performance, enabling tasks such as text recognition, image-based data extraction, and dynamic file modifications.

---

## 1. Integrating Computer Vision with AI Applications

### 1.1 Image Preprocessing for Enhanced OCR Accuracy

#### 1.1.1 Purpose
Improve text clarity and recognition accuracy by preprocessing images before applying OCR.

#### 1.1.2 Key Code Snippet
```python
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import cv2
import numpy as np

def preprocess_image(image_path: str, mode: str = 'auto') -> Image.Image:
    # Load image
    image = Image.open(image_path)
    
    # Convert to grayscale
    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray)
    
    # Auto mode preprocessing
    if mode == 'none':
        return image.convert('RGB')
    if mode == 'gray':
        return gray
    if mode == 'threshold':
        return gray.point(lambda p: 255 if p > 145 else 0, mode='L')
    if gray.width < 1400:
        factor = min(2.0, 1400 / max(gray.width, 1))
        gray = gray.resize((int(gray.width * factor), int(gray.height * factor)), Image.Resampling.LANCZOS)
    return ImageEnhance.Contrast(gray.filter(ImageFilter.SHARPEN)).enhance(1.35)
```

### 1.2 OCR Integration for Text Recognition

#### 1.2.1 Purpose
Utilize Tesseract OCR to recognize and extract text from preprocessed images.

#### 1.2.2 Key Code Snippet
```python
import subprocess
import pytesseract

class OCRError(Exception):
    """Custom exception for OCR errors."""
    pass

def ocr_image(image: Image.Image, language: str = 'eng+chi_tra', psm: int = 6) -> str:
    # Save preprocessed image to temporary file
    temp_image_path = 'temp_preprocessed.png'
    image.save(temp_image_path)
    
    # Build Tesseract command
    config = f"--oem 3 --psm {psm}"
    text = pytesseract.image_to_string(image, lang=language, config=config)
    
    # Clean up temporary file
    import os
    os.remove(temp_image_path)
    
    return text
```

### 1.3 Post-processing for Text Refinement

#### 1.3.1 Purpose
Clean and refine OCR-extracted text for further analysis or correction.

#### 1.3.2 Key Code Snippet
```python
def clean_ocr_text(text: str) -> str:
    # Remove unnecessary whitespace
    cleaned_text = ' '.join(text.split())
    return cleaned_text
```

### 1.4 Placeholder Replacement for Dynamic File Modification

#### 1.4.1 Purpose
Use placeholders in configuration files and replace them with extracted data to generate final configurations.

#### 1.4.2 Key Code Snippet
```python
# Example: Replacing placeholders in a file
replacements = {
    '[TODO_TOKEN]': 'export const GOOGLE_TOKEN_URL=TOKURL;',
    '[TODO_USERINFO]': 'export const GOOGLE_USERINFO_URL=UINFOURL;',
    # ... other replacements
}
with open('config.ts', 'r') as file:
    content = file.read()
for placeholder, replacement in replacements.items():
    content = content.replace(placeholder, replacement)
with open('config.ts', 'w') as file:
    file.write(content)
```

## 2. AI and CV Integration for Enhanced Functionality

### 2.1 Full-Stack Development for AI and CV Applications

#### 2.1.1 API Client Integration for AI Services

##### 2.1.1.1 API Key and Base URL Management
- **Loading API Key**: Securely retrieve the API key from environment variables or a configuration file.
  ```python
  def _load_api_key() -> str:
      return os.getenv('MINIMAX_API_KEY') or open('api_key.txt').read().strip()
  ```
- **Loading Base URL**: Fetch the base URL for the AI API from environment variables or default to a predefined URL.
  ```python
  def _load_base_url() -> str:
      return os.getenv('MINIMAX_API_BASE_URL') or 'https://api.minimax.com'
  ```

##### 2.1.1.2 API Request Construction
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

##### 2.1.1.3 API Response Handling
- **Sending Requests**: Utilize the `requests` library to send POST requests to the AI API.
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

##### 2.1.1.4 Response Parsing
- **Parsing Script Response**: Extract the script from the AI response using a dedicated parsing function.
  ```python
  return _parse_script_response(response.text, response.json())
  ```

#### 2.1.2 Common Errors and Prevention
- **API Endpoint or Format Assumptions**: Always verify API endpoints and formats using tools like `curl` before making actual requests.
- **Unhandled API Exceptions**: Always check the response status code and handle exceptions to prevent application crashes.

#### 2.1.3 AI Output Parser

##### 2.1.3.1 Parsing Logic
- **Language Extraction**: Identify the programming language specified in the AI output.
  ```python
  language = 'python'
  for line in text.splitlines():
      if line.startswith('# language:'):
          language = line.split(':', 1)[1].strip()
          break
  ```
- **Explanation Extraction**: Extract any explanatory comments provided by the AI.
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

##### 2.1.3.2 Result Structuring
- **ScriptGenResult**: Encapsulate the parsed script, language, explanation, and raw response.
  ```python
  return ScriptGenResult(script=body.strip(), language=language, explanation=explanation, raw=raw)
  ```

#### 2.1.4 Common Errors and Prevention
- **Unstable AI Output Formats**: Implement fault-tolerant parsing strategies, such as extracting headers first and handling fencing and footer explanations conditionally.
- **Mismatched Fencing Marks**: Ensure that markdown fencing marks are properly paired and handle cases where only the opening fence is present.

### 2.2 Integration and Workflow

#### 2.2.1 CLI Integration
- **Command-Line Interface**: Develop a CLI to accept user inputs, trigger the AI and CV services, and display or store the generated outputs.
  ```python
  import argparse
  import sys
  from ai_api_client import generate_script
  from ai_output_parser import ScriptGenResult

  def main():
      parser = argparse.ArgumentParser(description='Generate scripts using AI and CV services')
      parser.add_argument('ocr_text', help='OCR text input')
      parser.add_argument('user_intent', help='User intent for script generation')
      args = parser.parse_args()

      script_result = generate_script(args.ocr_text, args.user_intent)
      print(f'Language: {script_result.language}')
      print(f'Explanation: {script_result.explanation}')
      print(f'Script:\n{script_result.script}')

  if __name__ == '__main__':
      main()