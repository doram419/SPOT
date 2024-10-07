import io
import requests
from PIL import Image
import pytesseract

def perform_ocr_from_url(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"OCR 처리 중 오류 발생: {e}")
        return None