# Advanced OCR Integration

## Overview
This micro-skill focuses on integrating advanced Optical Character Recognition (OCR) and media transcription solutions into applications using Tesseract, Pytesseract, and the Whisper API. The goal is to achieve high accuracy, real-time processing, and support for multiple languages across various media formats, including images and audio.

---

## 1. Tesseract OCR Integration

### Description
Integrate the Tesseract OCR engine to extract text from images and scanned documents.

### Key Code Snippets and Patterns

#### Using Tesseract.js in JavaScript
```javascript
async function performOCR(imagePath) {
  try {
    const { Tesseract } = window;
    const worker = await Tesseract.createWorker({
      logger: (m) => console.log(m)
    });
    await worker.load();
    await worker.loadLanguage('eng+chi_tra'); // Load English and Traditional Chinese
    await worker.initialize('eng+chi_tra');
    const { data: { text } } = await worker.recognize(imagePath);
    await worker.terminate();
    return text;
  } catch (error) {
    console.error('Tesseract OCR error:', error);
    throw error;
  }
}
```

#### Using pytesseract in Python
```python
import pytesseract
from PIL import Image

def perform_ocr(image_path, lang='eng', psm=3):
    try:
        img = Image.open(image_path)
        data = pytesseract.image_to_data(
            img,
            lang=lang,
            config=f"--psm {psm} --oem 1",
            output_type=pytesseract.Output.DICT,
        )
        words = [w for w, c in zip(data["text"], data["conf"]) if w.strip() and int(c) >= 0]
        return ' '.join(words)
    except Exception as e:
        print(f"OCR error: {e}")
        raise e
```

### Common Errors and Prevention
- **Error**: Language pack not loaded.
  - **Solution**: Ensure that the required language packs are loaded using the `loadLanguage` method in Tesseract.js or correctly specified in the `lang` parameter in pytesseract. Include multiple languages by concatenating language codes with a '+' sign (e.g., 'eng+chi_tra').
  
- **Error**: Image quality is too low for accurate OCR.
  - **Solution**: Preprocess images to enhance quality. Techniques include adjusting contrast, resizing, or applying filters before passing them to the OCR engine.

- **Error**: Image format unsupported or corrupted.
  - **Solution**: Verify image format and integrity before processing. Use libraries like Pillow in Python to handle image opening and verification.

---

## 2. Whisper API Integration for Audio Transcription

### Description
Integrate OpenAI's Whisper API to achieve high-accuracy speech-to-text transcription.

### Key Code Snippets and Patterns
```javascript
async function transcribeWithWhisper(file, apiKey, language) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('model', 'whisper-1');
  formData.append('language', language); // Specify the language code, e.g., 'en' for English

  try {
    const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`
      },
      body: formData
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error?.message || 'API request failed');
    }

    return data.text; // Return the transcribed text
  } catch (error) {
    console.error('Whisper API error:', error);
    throw error; // Re-throw the error for further handling
  }
}
```

### Common Errors and Prevention
- **Error**: API key is exposed on the frontend.
  - **Solution**: In production environments, avoid exposing the API key by routing requests through a secure backend proxy. This ensures that the API key remains confidential.
  
- **Error**: Network requests fail or CORS issues arise.
  - **Solution**: Ensure that the server is correctly configured to handle cross-origin requests. Implement proper error handling to manage network-related issues gracefully.

---

## 3. Real-Time Audio Transcription in the Browser

### Description
Leverage the browser's SpeechRecognition API to enable low-latency, real-time speech-to-text functionality.

### Key Code Snippets and Patterns
```javascript
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.lang = 'zh-TW'; // Set the desired language code
recognition.continuous = true; // Enable continuous recognition
recognition.interimResults = true; // Allow interim results

recognition.onresult = (event) => {
  let interim = '';
  let final = '';
  for (let i = event.resultIndex; i < event.results.length; i++) {
    if (event.results[i].isFinal) {
      final += event.results[i][0].transcript;
    } else {
      interim += event.results[i][0].transcript;
    }
  }
  // Update the user interface with interim and final results
  updateUI(interim, final);
};

recognition.onerror = (event) => {
  console.error('Error:', event.error);
  // Handle errors gracefully, such as displaying a notification to the user
};

recognition.onend = () => {
  // Restart recognition if needed
  recognition.start();
};

recognition.start();
```

### Common Errors and Prevention
- **Error**: Browser does not support the SpeechRecognition API.
  - **Solution**: Before initializing, check if the API is available using feature detection. Provide a fallback solution, such as integrating the Whisper API via a backend service.
  
- **Error**: Speech recognition stops or fails to continue.
  - **Solution**: Ensure that the `continuous` property is set to `true`. Handle the `onend` event to automatically restart recognition as needed.

---

## 4. Error Prevention and Best Practices

### General Guidelines
- **API Key Security**: Never expose sensitive API keys on the client side. Use environment variables and secure backend proxies to handle API requests.
  
- **Error Handling**: Implement comprehensive error handling to manage different types of errors, including network issues, API failures, and processing errors. Provide meaningful feedback to users when errors occur.
  
- **Performance Optimization**: For real-time applications, ensure that the processing is optimized for performance. Use Web Workers or similar technologies to prevent blocking the main thread.
  
- **Language Support**: Clearly specify the language codes and ensure that the chosen tools support the target languages. Load necessary language packs and models as required.

### Security Considerations
- **Data Privacy**: Handle user data responsibly. Ensure compliance with data protection regulations, such as GDPR or CCPA, when processing and storing transcription results.
  
- **Secure Communication**: Use HTTPS to encrypt data in transit, especially when transmitting audio files or sensitive information to external APIs.

---

## 5. OCR Pipeline Integration

### Description
Integrate document monitoring events with the OCR processing pipeline to automatically perform OCR on new images and persist the results.

### Key Code Snippets
```python
class OCRPipeline:
    def __init__(self, watch_dir: str | Path, out_jsonl: str | Path, out_db: str | Path, preferred_lang: str | None = None):
        ...

    def _persist(self, result: OCRResult) -> None:
        # Write to JSONL
        with self.out_jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")
        # Write to SQLite
        with self._db_lock:
            self._conn.execute(
                "INSERT INTO ocr_results (ts,path,text,confidence,language,duration_ms,chars,error)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (...
            )
            self._conn.commit()
```

### Common Errors and Prevention
- **Error**: Database connection not managed correctly, leading to resource leaks.
  - **Solution**: Explicitly close the database connection when the pipeline stops.
  
- **Error**: Exceptions during processing cause the pipeline to crash.
  - **Solution**: Implement exception handling and retry mechanisms in critical steps.

---

## Conclusion
By integrating Tesseract, Pytesseract, and the Whisper API, this micro-skill provides a comprehensive solution for OCR and media transcription tasks. Adhering to best practices and error prevention strategies ensures high accuracy, real-time processing, and secure handling of user data across multiple languages.