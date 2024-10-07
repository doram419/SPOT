import io
import requests
from PIL import Image
import pytesseract
from typing import Optional

def perform_ocr_from_url(image_url: str) -> Optional[str]:
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        with Image.open(io.BytesIO(response.content)) as image:
            text = pytesseract.image_to_string(image)
        
        return text.strip() if text else None
    
    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 중 오류 발생: {e}")
    except IOError as e:
        print(f"이미지 열기 중 오류 발생: {e}")
    except pytesseract.TesseractError as e:
        print(f"OCR 처리 중 오류 발생: {e}")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
    
    return None