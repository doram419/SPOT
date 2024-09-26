from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.crawling.naver_service import fetch_naver_blog_data
from app.bert_service import get_embedding
import faiss
import numpy as np

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

# POST 요청을 통해 검색을 처리하는 엔드포인트
@router.post("/search/", response_class=HTMLResponse)
async def search_restaurant(request: Request, search_input: str = Form(...)):
    if not search_input:
        raise HTTPException(status_code=400, detail="검색어를 입력하세요.")

    print(f"검색어: {search_input}")

    try:
        # 네이버 블로그 데이터 가져오기
        region = "서울"  # 기본 지역 설정
        keywords = search_input.split()  # 검색어를 키워드로 사용
        naver_results = fetch_naver_blog_data(query=search_input, region=region, keywords=keywords)

        if not naver_results:
            raise HTTPException(status_code=404, detail="검색 결과가 없습니다.")

        # 임베딩 벡터 생성 및 FAISS 인덱스 추가
        embeddings = []
        valid_results = []
        for result in naver_results:
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

        # 디버깅: 임베딩 차원 확인
        print(f"변환 전 임베딩 차원: {embeddings.shape}")

        # 임베딩 벡터가 (n, 1, 768)이므로 (n, 768)으로 변환
        embeddings = embeddings.reshape(-1, dimension)

        # 디버깅: 변환 후 임베딩 차원 확인
        print(f"변환 후 임베딩 차원: {embeddings.shape}")

        # FAISS 인덱스에 벡터 추가
        index.add(embeddings)

        # 검색어의 임베딩 생성
        query_embedding = get_embedding(search_input).reshape(1, dimension)

        # 디버깅: 쿼리 임베딩 확인
        print(f"쿼리 임베딩 차원: {query_embedding.shape}")

        # FAISS로 유사한 검색 결과 찾기
        distances, indices = index.search(query_embedding, k=5)

        # 디버깅: 검색 결과 확인
        print(f"검색된 거리(distances): {distances}")
        print(f"검색된 인덱스(indices): {indices}")

        # 검색된 인덱스에 맞는 결과 추출
        best_results = [valid_results[i] for i in indices[0]]  # 가장 유사한 결과 5개 선택

        # 검색 결과를 최신순으로 정렬 (postdate로)
        sorted_results = sorted(best_results, key=lambda x: x.views, reverse=True)

        # 검색 결과 렌더링
        return templates.TemplateResponse("index.html", {
            "request": request,
            "search_results": sorted_results  # 템플릿에 검색 결과 전달
        })

    except Exception as e:
        print(f"검색 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="검색 중 오류가 발생했습니다.")