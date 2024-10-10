import io
import requests
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
from typing import Optional
import matplotlib.pyplot as plt
from paddleocr import PaddleOCR

DEBUG_MODE = True

# PaddleOCR 초기화 (한국어 사용 설정)
ocr = PaddleOCR(use_angle_cls=True, lang='korean', use_gpu=False, show_log=False)

def preprocess_image(image: Image.Image) -> Optional[Image.Image]:
    """이미지 전처리 함수"""
    try:
        print("전처리 Step 1: 이미지 해상도 확대")
        image = image.resize((image.width * 2, image.height * 1), Image.LANCZOS)

        print("전처리 Step 2: 대비 조정")
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2)

        print("전처리 Step 3: 샤프닝 필터 적용")
        image = image.filter(ImageFilter.SHARPEN)

        print("전처리 Step 4: 이미지 NumPy 배열로 변환")
        img_array = np.array(image)
        print(f"이미지 배열 형태: {img_array.shape}, 데이터 타입: {img_array.dtype}")

        print("전처리 Step 5: Grayscale 변환")
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        print("전처리 Step 6: GaussianBlur 적용")
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        print("전처리 Step 7: Adaptive Threshold 적용")
        adaptive_thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
        print("전처리 Step 8: 대비 증강")
        pil_image = Image.fromarray(adaptive_thresh)
        enhancer = ImageEnhance.Contrast(pil_image)
        enhanced_image = enhancer.enhance(3)

        print("전처리 Step 9: 샤프닝 필터 적용")
        enhanced_image_array = np.array(enhanced_image)
        sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened_image = cv2.filter2D(enhanced_image_array, -1, sharpen_kernel)
    
        if DEBUG_MODE:
            plt.imshow(sharpened_image, cmap='gray')
            plt.title('Preprocessed Image')
            plt.axis('off')
            #plt.show()

        final_image = Image.fromarray(sharpened_image)
        print("전처리 완료: 이미지 변환 성공")
        return final_image
    except Exception as e:
        print(f"전처리 중 오류 발생: {e}")
        return None

def perform_ocr_from_url(image_url: str) -> Optional[str]:
    """이미지 URL에서 OCR 수행"""
    try:
        print(f"Step 1: 이미지 다운로드 시작 - URL: {image_url}")
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        print("Step 2: 이미지 다운로드 완료")

        print("Step 3: 이미지 열기 시작")
        with Image.open(io.BytesIO(response.content)) as image:
            print(f"이미지 정보: 크기 {image.size}, 모드 {image.mode}")
            print("Step 4: 이미지 전처리 시작")
            processed_image = preprocess_image(image)
            
            if processed_image is None:
                print("이미지 전처리 실패")
                return None
            
            print("Step 5: 전처리된 이미지를 NumPy 배열로 변환")
            img_array = np.array(processed_image)
            print(f"전처리된 이미지 배열 형태: {img_array.shape}, 데이터 타입: {img_array.dtype}")

            print("Step 6: OCR 수행 시작")
            results = ocr.ocr(img_array, cls=True)
            print("Step 7: OCR 수행 완료")

            extracted_texts = []
            for idx, result in enumerate(results):
                print(f"결과 {idx + 1}:")
                for line in result:
                    if line is not None and len(line) > 1:
                        text, confidence = line[1][0], line[1][1]
                        print(f"  텍스트: {text}, 신뢰도: {confidence:.2f}")
                        if confidence >= 0.8:
                            filtered_text = ''.join(filter(lambda c: c.isalnum() or c.isspace(), text))
                            extracted_texts.append(filtered_text)
            
            text = ' '.join(extracted_texts)
            print(f"추출된 전체 텍스트: {text}")
        
        processed_text = post_process_text(text)
        print(f"후처리된 텍스트: {processed_text}")
        return processed_text.strip() if processed_text else None

    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 중 오류 발생: {e}")
    except IOError as e:
        print(f"이미지 열기 중 오류 발생: {e}")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
    
    return None

def post_process_text(text: str) -> str:
    """텍스트 후처리 함수: 숫자나 특정 단어만 남기기 등"""
    processed_text = ''.join(filter(lambda x: x.isdigit() or '가' <= x <= '힣' or x.isspace(), text))
    return processed_text
