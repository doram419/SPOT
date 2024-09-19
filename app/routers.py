from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.gpt_service import extract_keywords
from app.crawling.google_service import fetch_top_restaurants_nearby
from app.crawling.naver_service import fetch_naver_blog_data

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/search/", response_class=HTMLResponse)
async def search_restaurant(request: Request, query: str = Form(...), region: str = Form(...)):
    try:
        # 입력된 문장에서 핵심 키워드 추출
        keywords = extract_keywords(query)

        # 네이버 블로그 데이터 조회수 순으로 5개 가져오기
        naver_results = fetch_naver_blog_data(query, region, keywords)

        # Google Places 데이터 리뷰 많고 평점 좋은 순으로 5개 가져오기
        google_results = fetch_top_restaurants_nearby(query, region)

        # 네이버 블로그와 Google Places 데이터를 결합하여 반환
        combined_results = naver_results + google_results

        # 검색 결과를 템플릿에 전달하여 렌더링
        return templates.TemplateResponse("index.html", {
            "request": request,
            "search_results": combined_results
        })

    except Exception as e:
        print(f"오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 오류 발생: {str(e)}")
