import os
from PIL import Image
import pytesseract
from typing import List, Dict

class OCRProcessor:
    def __init__(self, tesseract_cmd_path: str = r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
        # Tesseract 실행 파일 경로 설정 (Windows 기준)
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path

    def process_image(self, image_path: str) -> str:
        """
        이미지 파일에서 텍스트를 추출합니다.
        
        :param image_path: 처리할 이미지 파일의 경로
        :return: 추출된 텍스트
        """
        try:
            with Image.open(image_path) as img:
                text = pytesseract.image_to_string(img, lang='kor')
                return text.strip()
        except Exception as e:
            print(f"Error processing image {image_path}: {str(e)}")
            return ""

    def process_directory(self, directory_path: str) -> List[Dict[str, str]]:
        """
        지정된 디렉토리 내의 모든 이미지 파일을 처리합니다.
        
        :param directory_path: 처리할 이미지가 있는 디렉토리 경로
        :return: 파일 이름과 추출된 텍스트를 포함하는 딕셔너리 리스트
        """
        results = []
        for filename in os.listdir(directory_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                file_path = os.path.join(directory_path, filename)
                extracted_text = self.process_image(file_path)
                results.append({
                    "filename": filename,
                    "text": extracted_text
                })
        return results

# 사용 예시
if __name__ == "__main__":
    ocr = OCRProcessor()
    
    # 단일 이미지 처리
    single_image_path = "path/to/your/image.jpg"
    text = ocr.process_image(single_image_path)
    print(f"Extracted text from {single_image_path}:")
    print(text)
    
    # 디렉토리 내 모든 이미지 처리
    directory_path = "path/to/your/image/directory"
    results = ocr.process_directory(directory_path)
    for result in results:
        print(f"File: {result['filename']}")
        print(f"Extracted Text: {result['text'][:100]}...")  # 처음 100자만 출력
        print("-" * 50)