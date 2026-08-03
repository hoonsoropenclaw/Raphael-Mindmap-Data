# Responsive Dynamic Form Generation

## Overview
This micro-skill focuses on creating dynamic and responsive forms that adapt to various devices and data collection requirements. It combines document-based text extraction with dynamic form generation, leveraging Python for text extraction and JavaScript (with React and Tailwind CSS) for form manipulation, responsive design, and Single Page Application (SPA) architecture.

## Key Components

### 1. Dynamic Form Generation

#### Description
This component involves setting up a dynamic form generator that creates form fields based on a predefined schema or extracted document structure. It handles basic form operations, including adding, removing, and validating fields, and ensures the form is responsive across different devices.

#### Key Code Snippet
```javascript
// 表單 schema 定義
const formSchema = [
  { label: '姓名', key: 'name', type: 'text', required: true },
  { label: '年齡', key: 'age', type: 'number', required: false },
  // 更多字段
];

// 動態生成表單
function DynamicForm({ schema }) {
  const [fields, setFields] = useState([]);

  const addField = () => {
    setFields([...fields, { id: Date.now(), type: 'text', label: '新字段' }]);
  };

  const removeField = (id) => {
    setFields(fields.filter(field => field.id !== id));
  };

  return (
    <form>
      {schema.map(field => (
        <div key={field.key} className="mb-4">
          <label className="block mb-1">{field.label}</label>
          <input
            type={field.type}
            required={field.required}
            className="border border-gray-300 p-2 w-full"
          />
        </div>
      ))}
      <ul>
        {fields.map(field => (
          <li key={field.id} className="mb-2">
            <input
              type="text"
              value={field.label}
              onChange={(e) => {
                const newLabel = e.target.value;
                setFields(fields.map(f => f.id === field.id ? { ...f, label: newLabel } : f));
              }}
              className="border border-gray-300 p-2 w-full"
            />
            <button
              onClick={() => removeField(field.id)}
              className="ml-2 bg-red-500 text-white px-2 py-1"
            >
              刪除
            </button>
          </li>
        ))}
      </ul>
      <button
        type='submit'
        className="bg-blue-500 text-white px-4 py-2"
      >
        提交
      </button>
      <button
        onClick={addField}
        className="ml-2 bg-green-500 text-white px-4 py-2"
      >
        新增字段
      </button>
    </form>
  );
}
```

#### Common Errors and Prevention
- **Error**: Unsupported form field types.
  **Solution**: Ensure all necessary form field types are explicitly defined in the schema and handle them appropriately during form generation.
- **Error**: Inadequate form validation.
  **Solution**: Implement strict validation during form submission to ensure data integrity and correctness.
- **Error**: Form data is not saved or synchronized correctly.
  **Solution**: Use React state management to track changes and ensure data is passed to the backend or other processing as needed.
- **Error**: Dynamically added fields do not render correctly.
  **Solution**: Assign a unique `id` to each field and use the `key` attribute correctly during rendering.

### 2. Document-Based Text Extraction

#### PDF Text Extraction

##### Description
The `pypdf` library is used to extract text from PDF files.

###### Key Code Snippet
```python
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        return ""
```

###### Common Errors and Prevention
- **Error**: Encrypted or specially encoded PDFs may prevent text extraction.
  **Solution**: Implement exception handling to catch and log problematic files for further processing.

#### Tesseract OCR Integration for Image Files

##### Description
Tesseract OCR, integrated via the `pytesseract` library, extracts text from image files.

###### Key Code Snippet
```python
from PIL import Image
import pytesseract

def extract_text_from_image(image_path: str, lang: str = 'chi_tra') -> str:
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=lang)
        return text
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return ""
```

###### Configuration
- **Language**: The `lang` parameter specifies the text language. For Traditional Chinese, use `'chi_tra'`. Adjust based on document language.

###### Common Errors and Prevention
- **Error**: Unsupported or corrupted image formats can cause OCR failure.
  **Solution**: Verify image formats before processing and include exception handling to manage errors gracefully.

#### Unified Extraction Process

##### Description
A unified function detects the file type and applies the appropriate extraction method for both PDF and image files.

###### Key Code Snippet
```python
from pypdf import PdfReader
from PIL import Image
import pytesseract
import os

def extract_text(file_path: str, lang: str = 'chi_tra') -> str:
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return ""
    
    if file_path.lower().endswith('.pdf'):
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text
        except Exception as e:
            print(f"Error processing PDF {file_path}: {e}")
            return ""
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang=lang)
            return text
        except Exception as e:
            print(f"Error processing image {file_path}: {e}")
            return ""
    else:
        print(f"Unsupported file format for file {file_path}.")
        return ""
```

###### Usage Example
```python
file_path = 'path/to/your/document.pdf'  # or 'path/to/your/image.png'
extracted_text = extract_text(file_path)
print(extracted_text)
```

##### Additional Considerations

###### Dependencies Installation
- **Python Libraries**: Install using `pip`:
  ```bash
  pip install pypdf pytesseract pillow
  ```
- **Tesseract OCR Engine**: Install via system package manager:
  - **Windows**: Download from [Tesseract OCR GitHub](https://github.com/tesseract-ocr/tesseract) and follow instructions.
  - **macOS**: Use Homebrew:
    ```bash
    brew install tesseract
    ```
  - **Linux**: Use distribution's package manager, e.g.,
    ```bash
    sudo apt-get install tesseract-ocr
    ```

###### Language Pack
For non-English languages, install appropriate language packs, e.g., for Traditional Chinese, install `tessdata` with `chi_tra` support.

###### Performance Optimization
- **Batch Processing**: Process multiple files in batches for improved performance.
- **Multithreading**: Utilize multithreading or multiprocessing to parallelize extraction.

###### Error Handling
Implement comprehensive error handling to manage issues like missing files, unsupported formats, or OCR failures.

### 3. Single File SPA Architecture

#### Purpose
Utilize a single-file SPA architecture to implement the dynamic form generator, ensuring the deliverable is easy to deploy and validate.

#### Key Code Snippet or Patterns
```
1. Use CDN to include React and Tailwind CSS.
2. Write all components and logic into a single HTML file.
3. Use Babel to transpile JSX into browser-readable JavaScript.
4. Use localStorage for data persistence.
5. Implement responsive design to ensure good display on different devices.
```

#### Common Errors and Prevention
- **Error**: Single file is too large, causing slow loading.
  **Solution**: Optimize code structure, use code compression and code-splitting techniques.
- **Error**: Lack of accessibility design, affecting user experience.
  **Solution**: Follow accessibility design guidelines, such as using ARIA labels and keyboard navigation.

## Conclusion
By integrating text extraction with dynamic form generation and establishing a single-file SPA architecture, this micro-skill enables the creation of efficient and flexible data collection tools. Users can implement these techniques in their projects by following the provided guidelines and utilizing the code snippets.

---

# Responsive UI Design

## Description
### Purpose
Use Tailwind CSS's breakpoint system to implement responsive layouts across different devices, ensuring the UI displays well on desktops, tablets, and mobile devices.

## Key Code Snippets or Patterns
```html
<div class="flex flex-col md:flex-row">
  <!-- Content -->
</div>
```

## Common Errors and Prevention
- **Error**: Incorrect use of breakpoint classes leading to layout issues on different devices.
  **Solution**: Familiarize yourself with Tailwind CSS's breakpoint classes (such as `sm:`, `md:`,