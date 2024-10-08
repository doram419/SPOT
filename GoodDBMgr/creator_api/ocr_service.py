import io
import requests
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2
import numpy as np
from typing import Optional

def preprocess_image(image: Image.Image) -> Image.Image:
    img_array = np.array(image)

    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morph = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel)

    pil_image = Image.fromarray(morph)
    enhancer = ImageEnhance.Contrast(pil_image)
    enhanced_image = enhancer.enhance(2)
    
    return enhanced_image

def perform_ocr_from_url(image_url: str) -> Optional[str]:
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        with Image.open(io.BytesIO(response.content)) as image:
            # 이미지 전처리 합니다
            processed_image = preprocess_image(image)
            # OCR 수행
            custom_config = r'--oem 3 --psm 6 -l kor'
            text = pytesseract.image_to_string(processed_image, config=custom_config)
        
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

