# OCR Application Development

## Purpose
Integrate OCR capabilities into applications for real-time text recognition from images.

## Key Code Snippets/Patterns
```python
from PIL import Image
import pytesseract

def preprocess_image(image: Image.Image, mode: str = 'auto') -> Image.Image:
    if mode == 'none':
        return image.convert('RGB')
    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray)
    if mode == 'gray':
        return gray
    if mode == 'threshold':
        return gray.point(lambda p: 255 if p > 145 else 0, mode='L')
    # auto mode
    if gray.width < 1400:
        factor = min(2.0, 1400 / max(gray.width, 1))
        gray = gray.resize((int(gray.width * factor), int(gray.height * factor)), Image.Resampling.LANCZOS)
    return ImageEnhance.Contrast(gray.filter(ImageFilter.SHARPEN)).enhance(1.35)

def perform_ocr(image: Image.Image, lang: str = 'eng', psm: int = 6) -> dict:
    config = f"--oem 3 --psm {psm}"
    text = pytesseract.image_to_string(image, lang=lang, config=config)
    return {"text": text}
```

## Common Errors & Solutions
- **Error**: Unsupported image formats or corrupted images.
  **Solution**: Use `try-except` blocks to catch `UnidentifiedImageError` and validate image data before processing.
- **Error**: Tesseract language packs not installed.
  **Solution**: Check available languages using `pytesseract.get_languages()` and provide user feedback if a requested language is unavailable.