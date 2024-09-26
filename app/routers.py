from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.crawling.naver_service import fetch_naver_blog_data
from app.bert_service import get_embedding
import faiss
import numpy as np
import asyncio

# FAISS 설정
dimension = 768
index = faiss.IndexFlatL2(dimension)


# FastAPI의 APIRouter 인스턴스 생성
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# GET 요청 처리, 메인 페이지 렌더링
@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 비동기로 네이버 블로그 데이터 가져오기
async def fetch_blog_data(query: str, region: str, keywords: list):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fetch_naver_blog_data, query, region, keywords)

# POST 요청을 통해 검색을 처리하는 엔드포인트
@router.post("/search/", response_class=HTMLResponse)
async def search_restaurant(request: Request, search_input: str = Form(...)):
    if not search_input:
        raise HTTPException(status_code=400, detail="검색어를 입력하세요.")

    print(f"검색어: {search_input}")

    try:
        region = "서울"  # 기본 지역 설정
        keywords = search_input.split()  # 검색어를 키워드로 사용

        # 비동기로 네이버 블로그 데이터 가져오기
        naver_results = await fetch_blog_data(search_input, region, keywords)

        if not naver_results:
            raise HTTPException(status_code=404, detail="검색 결과가 없습니다.")

        # 임베딩 벡터 생성 및 FAISS 인덱스 추가
        embeddings = []
        valid_results = []
        for i, result in enumerate(naver_results):
            title = result.title if result.title else ""
            description = result.description if result.description else ""
            combined_text = title + " " + description

            if combined_text.strip():  # 빈 문자열이 아닌 경우에만 처리
                embedding = get_embedding(combined_text)
                embeddings.append(embedding)
                valid_results.append(result)

        if len(embeddings) == 0:
            raise HTTPException(status_code=500, detail="유효한 블로그 데이터가 없습니다.")

        embeddings = np.array(embeddings, dtype='float32')

        # FAISS에 추가된 벡터 확인
        print(f"임베딩 차원: {embeddings.shape}")
        embeddings = embeddings.reshape(-1, dimension)

        # FAISS 인덱스에 벡터 추가
        index.add(embeddings)

        # 검색어의 임베딩 생성
        query_embedding = get_embedding(search_input).reshape(1, dimension)

        # FAISS로 유사한 검색 결과 찾기
        distances, indices = index.search(query_embedding, k=5)


        # 유효한 인덱스만 선택 (index out of range 방지)
        valid_indices = [i for i in indices[0] if i < len(valid_results)]

        print(f"검색된 유효한 인덱스: {valid_indices}")

        # 검색된 유효한 인덱스에 맞는 결과 추출
        best_results = [valid_results[i] for i in valid_indices]

        # 검색 결과를 정렬할 때 None 값을 처리 (views 값이 None이면 기본값을 설정)
        sorted_results = sorted(best_results, key=lambda x: x.views if x.views is not None else 0, reverse=True)

        # 검색 결과 렌더링
        return templates.TemplateResponse("index.html", {
            "request": request,
            "search_results": sorted_results  # 템플릿에 검색 결과 전달
        })

    except Exception as e:
        print(f"검색 중 오류 발생: {str(e)}")

        raise HTTPException(status_code=500, detail="검색 중 오류가 발생했습니다.")

