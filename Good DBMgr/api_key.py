# API 키를 환경변수로 관리하기 위한 설정 파일
import os
from dotenv import load_dotenv

# API 키 정보 로드
load_dotenv()

class Api_Key():
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")

    def check_status(self) -> dict : 
        return dict(
            "openAI-Key", True if self.openai_key else False
        )