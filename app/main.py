from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Optional
import os
import re
import requests
import urllib.parse
import googlemaps
import openai
import numpy as np
import torch
from transformers import BertTokenizer, BertModel

# .env 파일에서 환경 변수 로드
load_dotenv()

# API 키 및 자격 증명을 환경 변수에서 불러옴
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# OpenAI API 키 설정
openai.api_key = OPENAI_API_KEY

# Google Maps 클라이언트 초기화
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# 정적 파일 및 템플릿 디렉토리 설정
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="templates")

# 모든 도메인에서의 접근을 허용하기 위한 CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# BERT 모델 및 토크나이저 로드
tokenizer = BertTokenizer.from_pretrained('klue/bert-base')
bert_model = BertModel.from_pretrained('klue/bert-base')


# 검색 결과 모델 정의
class SearchResult(BaseModel):
    title: str
    link: str
    description: str
    rating: Optional[float] = None
    views: Optional[int] = None  # 조회수를 추가


# Google Geocoding API를 사용하여 지역명을 위도 및 경도로 변환하는 함수
def get_coordinates(region: str):
    geocode_result = gmaps.geocode(region)
    if geocode_result and 'geometry' in geocode_result[0]:
        location = geocode_result[0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        raise HTTPException(status_code=404, detail="해당 지역을 찾을 수 없습니다.")


# Google Places API를 사용하여 리뷰가 많고 평점이 좋은 순으로 장소 5개를 검색하는 함수
def fetch_google_places(query: str, region: str) -> List[SearchResult]:
    try:
        lat, lng = get_coordinates(region)
        places_result = gmaps.places_nearby(location=(lat, lng), radius=1000, keyword=query)

        results = []
        for place in places_result.get('results', []):
            place_id = place.get('place_id')
            place_details = gmaps.place(place_id=place_id, fields=['name', 'rating', 'user_ratings_total', 'url'])

            if place_details:
                place_name = place_details['result'].get('name', 'N/A')
                place_url = place_details['result'].get('url', '#')
                place_rating = place_details['result'].get('rating', 0)
                reviews_total = place_details['result'].get('user_ratings_total', 0)

                results.append(SearchResult(
                    title=place_name,
                    link=place_url,
                    description="Google Places 리뷰",
                    rating=place_rating,
                    views=reviews_total  # 리뷰 수를 조회수로 사용
                ))

        # 리뷰 개수와 평점을 기준으로 정렬 후 상위 5개만 반환
        return sorted(results, key=lambda x: (x.views, x.rating), reverse=True)[:5]

    except Exception as e:
        print(f"Google Places API 요청 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="Google Places API에서 데이터를 가져오지 못했습니다.")


# 네이버 블로그 데이터를 조회수 높은 순으로 5개 가져오는 함수
def fetch_naver_blog_data(query: str, region: str) -> List[SearchResult]:
    try:
        enc_text = urllib.parse.quote(query)
        url = f"https://openapi.naver.com/v1/search/blog?query={enc_text}"

        headers = {
            "X-Naver-Client-Id": CLIENT_ID,
            "X-Naver-Client-Secret": CLIENT_SECRET
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        items = response.json().get("items", [])
        results = [
            SearchResult(
                title=clean_html(item['title']),
                link=item['link'],
                description=clean_html(item['description']),
                views=int(re.search(r'\d+', item.get('postdate', '0')).group())  # 조회수를 추출 (임시로 게시 날짜 사용)
            )
            for item in items if region in clean_html(item['description'])
        ]

        # 조회수 순으로 정렬 후 상위 5개만 반환
        return sorted(results, key=lambda x: x.views, reverse=True)[:5]

    except requests.exceptions.RequestException as e:
        print(f"Naver API 요청 실패: {str(e)}")  # 오류 로그 출력
        raise HTTPException(status_code=500, detail="네이버 API에서 데이터를 가져오지 못했습니다.")
    except Exception as e:
        print(f"일반 오류 발생: {str(e)}")  # 기타 오류 로그 출력
        raise HTTPException(status_code=500, detail="네이버 블로그 데이터를 처리하는 중 오류가 발생했습니다.")


# HTML 태그를 정규식으로 제거하는 함수
def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


# 긴 문장을 청크로 나누는 함수
def chunk_text(text: str, chunk_size=512):
    tokens = tokenizer.tokenize(text)
    return [' '.join(tokens[i:i + chunk_size]) for i in range(0, len(tokens), chunk_size)]


# BERT 임베딩 생성 함수
def get_embedding(text: str):
    """BERT 임베딩 생성 함수"""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = bert_model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).numpy()


def extract_keywords(text: str):
    """OpenAI GPT를 사용하여 문장에서 핵심 키워드를 추출하는 함수"""
    try:
        chunks = chunk_text(text)
        keywords = []

        for chunk in chunks:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts keywords."},
                    {"role": "user", "content": f"Extract keywords from the following text: {chunk}"}
                ]
            )
            keywords.append(response['choices'][0]['message']['content'].strip())

        return ' '.join(keywords)

    except Exception as e:
        print(f"키워드 추출 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="GPT 모델에서 키워드를 추출하지 못했습니다.")

# 루트 페이지 요청 처리
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 검색 요청 처리 엔드포인트
@app.post("/search/", response_class=HTMLResponse)
async def search_restaurant(request: Request, query: str = Form(...), region: str = Form(...)):
    try:
        # 입력된 문장에서 핵심 키워드를 추출
        keywords = extract_keywords(query)

        # 네이버 블로그 데이터 조회수 순으로 5개 가져오기
        naver_results = fetch_naver_blog_data(keywords, region)

        # Google Places 데이터 리뷰 많고 평점 좋은 순으로 5개 가져오기
        google_results = fetch_google_places(keywords, region)

        # 결합된 결과 반환
        combined_results = naver_results + google_results

        return templates.TemplateResponse("index.html", {
            "request": request,
            "search_results": combined_results
        })

    except Exception as e:
        print(f"오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"오류가 발생했습니다: {str(e)}")