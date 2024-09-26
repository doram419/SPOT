from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routers import router
from app.crawling.naver_service import fetch_naver_blog_data
from app.gpt_service import extract_keywords
from fastapi import FastAPI
from app.auth import router as auth_router  # auth 모듈에서 라우터를 임포트
from app.database import init_db
from app.models import User


# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()


# DB 초기화
init_db()

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

# 라우터 추가
app.include_router(auth_router)



# FastAPI 엔드포인트 추가

@app.get("/naver_blogs")
async def get_naver_blogs(query: str, keywords: str):
    """네이버 블로그 검색"""
    keywords_list = keywords.split(',')
    blogs = fetch_naver_blog_data(query, keywords_list)
    return {"blogs": blogs}


@app.post("/keywords")
async def extract_gpt_keywords(text: str):
    """GPT를 사용한 키워드 추출"""
    keywords = extract_keywords(text)
    return {"keywords": keywords}
