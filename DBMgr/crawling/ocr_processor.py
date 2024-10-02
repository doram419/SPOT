import pytesseract
import cv2
import os
from typing import Optional

os.environ['TESSDATA_PREFIX'] = r'C:/Program Files/Tesseract-OCR/tessdata/'

def process_image(image_path: str) -> Optional[str]:
    """
    이미지에서 텍스트를 추출하는 OCR 함수
    :param image_path: 처리할 이미지 파일의 경로
    :return: 추출된 텍스트 또는 None(에러 발생시)
    """
    try:
        # OpenCV로 이미지 읽기
        image = cv2.imread(image_path)

        if image is None:
            print(f"Error: 이미지 파일을 찾을 수 없습니다. 경로를 확인해주세요: {image_path}")
            return None
        # BGR 형식 이미지를 RGB 형식으로 변환 (OpenCV는 기본적으로 BGR 형식 사용)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # ocr 추출
        text = pytesseract.image_to_string(rgb_image, lang='kor+eng')

        return text.strip()
    
    except Exception as e:
        print(f"OCR 처리 중 오류 발생: {str(e)}")
        return None
    
# 테스트해보자
if __name__ == "__main__":
    test_image_path = ""  # 테스트할 이미지 경로지정하기
    result = process_image(test_image_path)
    if result:
        print("추출된 텍스트:")
        print(result)
    else:
        print("텍스트 추출 실패")