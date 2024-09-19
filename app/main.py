from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routers import router
from app.crawling.google_service import fetch_top_restaurants_nearby
from app.crawling.naver_service import fetch_naver_blog_data
from app.bert_service import get_embedding
from app.gpt_service import extract_keywords

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# 정적 파일 및 템플릿 경로 설정
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# CORS 설정 - 모든 도메인에서 접근 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(router)

# FastAPI 엔드포인트 추가
@app.get("/restaurants")
async def get_top_restaurants(query: str = "맛집", region: str = Query(..., description="검색할 지역")):
    """사용자가 입력한 지역에서 상위 5개의 맛집 검색"""
    top_restaurants = fetch_top_restaurants_nearby(query, region)
    return {"restaurants": top_restaurants}

@app.get("/naver_blogs")
async def get_naver_blogs(query: str, keywords: str):
    """네이버 블로그 검색"""
    keywords_list = keywords.split(',')
    blogs = fetch_naver_blog_data(query, keywords_list)
    return {"blogs": blogs}

@app.post("/embedding")
async def get_bert_embedding(text: str):
    """BERT 임베딩 생성"""
    embedding = get_embedding(text)
    return {"embedding": embedding.tolist()}  # numpy 배열은 리스트로 변환해야 JSON으로 반환 가능

@app.post("/keywords")
async def extract_gpt_keywords(text: str):
    """GPT를 사용한 키워드 추출"""
    keywords = extract_keywords(text)
    return {"keywords": keywords}
