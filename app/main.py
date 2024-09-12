from fastapi import FastAPI, HTTPException, Request, Form
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import re
import os
import googlemaps
from dotenv import load_dotenv
from typing import List
import requests
import urllib.parse

# .env 파일에서 환경 변수 로드 (API 키, 클라이언트 ID 등 환경 변수 사용)
load_dotenv()

# Google Maps API 키를 환경 변수에서 불러옴
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 네이버 API 클라이언트 ID와 시크릿을 환경 변수에서 불러옴
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# Google Maps 클라이언트 초기화
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# 정적 파일 및 템플릿 설정
# '/static' 경로에서 정적 파일 (CSS, JS)을 제공
app.mount("/static", StaticFiles(directory="app/static"), name="static")
# Jinja2 템플릿을 사용할 디렉토리 설정
templates = Jinja2Templates(directory="templates")

# CORS 설정 (모든 도메인에서 접근 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 검색 결과 모델 정의 (FastAPI가 사용하는 데이터 구조)
class SearchResult(BaseModel):
    title: str
    link: str
    description: str

# Google Places API에서 리뷰 데이터를 저장하는 모델 정의
class GooglePlaceReview(BaseModel):
    author_name: str
    rating: float
    text: str
    relative_time_description: str

# Google Geocoding API를 사용하여 지역명을 위도/경도로 변환하는 함수
def get_coordinates(region: str):
    """
    입력받은 지역명을 Google Geocoding API를 사용해 위도(lat)와 경도(lng)로 변환.
    지역명이 존재하지 않으면 404 오류를 반환합니다.
    """
    geocode_result = gmaps.geocode(region)
    if geocode_result and 'geometry' in geocode_result[0]:
        # 반환된 데이터에서 위도와 경도 추출
        location = geocode_result[0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        raise HTTPException(status_code=404, detail="해당 지역을 찾을 수 없습니다.")

# Google Places API로 장소 데이터 가져오기
def fetch_google_places(query: str, region: str) -> List[SearchResult]:
    """
    Google Places API를 사용해 지역의 맛집 데이터를 검색.
    지역을 위도와 경도로 변환하고 반경 1km 내에서 검색한 후, 리뷰가 좋은 순으로 정렬.
    """
    try:
        # 지역명을 위도와 경도로 변환
        lat, lng = get_coordinates(region)

        # Google Places API로 장소 검색 (위도와 경도, 반경 1km 내)
        places_result = gmaps.places_nearby(location=(lat, lng), radius=1000, keyword=query)

        results = []
        for place in places_result.get('results', []):
            # 각 장소에 대한 세부 정보를 가져옴 (평점, 리뷰 포함)
            place_id = place.get('place_id')
            place_details = gmaps.place(place_id=place_id, fields=['name', 'rating', 'reviews', 'url'])

            if place_details:
                # 결과에서 name, url, rating 정보 가져옴 (없는 경우 기본값 설정)
                place_name = place_details['result'].get('name', 'N/A')
                place_url = place_details['result'].get('url', '#')
                place_rating = place_details['result'].get('rating', 0)  # rating이 없으면 0으로 처리

                # 리뷰 데이터를 가져옴
                reviews = place_details['result'].get('reviews', [])

                # 리뷰 목록 구성
                review_list = [
                    GooglePlaceReview(
                        author_name=review.get('author_name', 'Unknown'),
                        rating=review.get('rating', 'N/A'),
                        text=review.get('text', 'No review'),
                        relative_time_description=review.get('relative_time_description', 'No date')
                    )
                    for review in reviews
                ]

                # 장소 데이터를 results에 추가
                results.append({
                    "title": place_name,
                    "link": place_url,
                    "rating": place_rating,
                    "reviews": review_list
                })

        # 평점이 높은 순서대로 정렬
        sorted_results = sorted(results, key=lambda x: x['rating'], reverse=True)

        # SearchResult 형식으로 변환하여 반환
        search_results = [
            SearchResult(
                title=item['title'],
                link=item['link'],
                description=f"Rating: {item['rating']}"
            )
            for item in sorted_results
        ]

        return search_results

    except Exception as e:
        # 오류 발생 시 로그 출력 및 500 오류 반환
        print(f"Google Places API 요청 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="Google Places API에서 데이터를 가져오지 못했습니다.")

# HTML 태그를 제거하는 함수
def clean_html(raw_html):
    """
    HTML 태그를 정규 표현식을 사용하여 제거.
    순수한 텍스트만 반환.
    """
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

# 네이버 블로그 데이터에서 지역명 필터링 함수
def filter_results_by_region(results, region):
    """
    네이버 블로그 데이터에서 title 또는 description에 입력한 지역명이 포함된 경우만 필터링하여 반환.
    """
    filtered_results = []
    for result in results:
        # 지역명이 포함된 데이터만 결과에 추가
        if region in result.title or region in result.description:
            filtered_results.append(result)
    return filtered_results

# 네이버 블로그 데이터를 가져오는 함수
def fetch_naver_blog_data(query: str, region: str) -> List[SearchResult]:
    """
    네이버 블로그 API를 사용해 검색어에 맞는 데이터를 가져옴.
    HTML 태그를 제거한 후 지역명으로 필터링된 데이터를 반환.
    """
    try:
        # 검색어를 URL 인코딩
        enc_text = urllib.parse.quote(query)
        # 네이버 블로그 API 요청 URL 구성
        url = f"https://openapi.naver.com/v1/search/blog?query={enc_text}"

        # API 요청 헤더 설정
        headers = {
            "X-Naver-Client-Id": CLIENT_ID,
            "X-Naver-Client-Secret": CLIENT_SECRET
        }

        # 네이버 블로그 API로 데이터 요청
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # API 응답에서 검색 결과 추출
        items = response.json().get("items", [])

        # 검색 결과에서 HTML 태그 제거 및 지역명 필터링
        filtered_items = filter_results_by_region([
            SearchResult(
                title=clean_html(item['title']),
                link=item['link'],
                description=clean_html(item['description'])
            )
            for item in items
        ], region)

        return filtered_items

    except requests.exceptions.RequestException as e:
        # API 요청 실패 시 로그 출력 및 500 오류 반환
        print(f"Naver API 요청 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="네이버 API에서 데이터를 가져오지 못했습니다.")

# 루트 페이지 요청 처리
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    루트 경로 ('/') 요청 시 index.html 템플릿을 렌더링하여 반환.
    """
    return templates.TemplateResponse("index.html", {"request": request})

# 검색 요청 처리 엔드포인트
@app.post("/search/", response_class=HTMLResponse)
async def search_restaurant(request: Request, query: str = Form(...), region: str = Form(...)):
    """
    사용자가 입력한 검색어(query)와 지역(region)을 기반으로
    네이버 블로그와 Google Places 데이터를 검색하여 결과를 반환.
    """
    try:
        # 네이버 검색어와 지역을 합친 검색어 생성
        full_query = f"{region} {query}"

        # 네이버 블로그 데이터 가져오기
        naver_results = fetch_naver_blog_data(full_query, region)

        # Google Places 데이터 가져오기 (지역을 위도/경도로 변환하여 검색)
        google_results = fetch_google_places(query, region)

        # 네이버와 구글 데이터를 결합
        combined_results = naver_results + google_results

        # 결합된 검색 결과 정리
        cleaned_results = [
            {
                "title": result.title,
                "description": result.description,
                "link": result.link
            }
            for result in combined_results
        ]

        # 템플릿에 검색 결과 전달하여 렌더링
        return templates.TemplateResponse("index.html", {
            "request": request,
            "search_results": cleaned_results
        })

    except Exception as e:
        # 오류 발생 시 로그 출력 및 500 오류 반환
        print(f"오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"오류가 발생했습니다: {str(e)}")
