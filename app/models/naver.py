import requests
import os
import urllib.parse
from dotenv import load_dotenv
from typing import List
from fastapi import HTTPException
from pydantic import BaseModel

# .env 파일에서 환경 변수 로드
load_dotenv()

# 네이버 API 클라이언트 ID와 시크릿을 환경 변수에서 가져옴
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 검색 결과 데이터 모델 정의
class SearchResult(BaseModel):
    title: str
    link: str
    description: str

def fetch_naver_blog_data(query: str) -> List[SearchResult]:
    try:
        enc_text = urllib.parse.quote(query)
        url = f"https://openapi.naver.com/v1/search/blog?query={enc_text}"

        headers = {
            "X-Naver-Client-Id": CLIENT_ID,
            "X-Naver-Client-Secret": CLIENT_SECRET
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 요청이 실패하면 예외 발생

        items = response.json().get("items", [])
        return [SearchResult(title=item['title'], link=item['link'], description=item['description']) for item in items]

    except requests.exceptions.RequestException as e:
        print(f"Naver API request failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch data from Naver API")
