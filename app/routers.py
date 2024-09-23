from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.gpt_service import extract_keywords
from app.crawling.google_service import fetch_top_restaurants_nearby
from app.crawling.naver_service import fetch_naver_blog_data
from app.bert_service import get_embedding
import faiss
import numpy as np

# FAISS 인덱스 초기화 (L2 거리 기반 인덱스)
dimension = 768  # 벡터 차원 수 (예: BERT 임베딩의 차원)
index = faiss.IndexFlatL2(dimension)


# 벡터 저장 함수
def store_vectors_in_faiss(vectors: np.ndarray):
    # FAISS는 2차원 배열을 요구하므로, 벡터 차원이 맞는지 확인
    if len(vectors.shape) > 2:
        # 불필요한 차원 제거 (예: (1, 1, 768) -> (1, 768))
        vectors = np.squeeze(vectors)
    # FAISS는 2차원 배열 형태의 벡터 입력을 요구함
    if len(vectors.shape) != 2 or vectors.shape[1] != dimension:
        raise ValueError(f"벡터의 차원이 올바르지 않습니다. 예상: 2D 배열 [{None}, {dimension}], 받은: {vectors.shape}")

    # 벡터를 FAISS 인덱스에 추가
    index.add(vectors)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/search/", response_class=HTMLResponse)
async def search_restaurant(request: Request, search_input: str = Form(...)):
    # 입력된 검색어에서 지역과 키워드 추출
    search_tokens = search_input.split()
    if len(search_tokens) < 2:
        raise HTTPException(status_code=400, detail="검색어와 지역을 모두 입력하세요.")

    region = search_tokens[0]  # 첫 번째 단어를 지역으로 간주
    query = ' '.join(search_tokens[1:])  # 나머지 단어를 검색어로 간주

    # 키워드 추출
    keywords = extract_keywords(query)

    # 네이버 블로그 및 구글 맛집 데이터 가져오기
    naver_results = fetch_naver_blog_data(query, region, keywords)
    google_results = fetch_top_restaurants_nearby(query, region)

    print(f"네이버 검색 결과: {len(naver_results)}개")
    print(f"구글 검색 결과: {len(google_results)}개")
    print(f"Google Places API 검색 결과: {google_results}")

    combined_results = naver_results + google_results

    # 임베딩 벡터 생성 (결과에 대한 임베딩 처리)
    embeddings = np.array([get_embedding(result.title + " " + result.description) for result in combined_results], dtype='float32')

    # 벡터의 차원이 올바른지 확인하고 2차원으로 변환
    if embeddings.ndim == 3:
        embeddings = embeddings.reshape(-1, dimension)  # (n, 1, 768) -> (n, 768)
    elif embeddings.ndim == 2:
        embeddings = embeddings
    elif embeddings.ndim == 1:
        embeddings = embeddings.reshape(1, dimension)  # 1D 벡터를 2D로 변환

    # FAISS는 2차원 배열을 요구하므로, 임베딩을 확인 후 저장
    store_vectors_in_faiss(embeddings)

    # 검색 결과 반환
    return templates.TemplateResponse("index.html", {
        "request": request,
        "search_results": combined_results
    })




# from fastapi import APIRouter, Request, Form, HTTPException
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from app.gpt_service import extract_keywords
# from app.crawling.google_service import fetch_top_restaurants_nearby
# from app.crawling.naver_service import fetch_naver_blog_data
# from app.bert_service import get_embedding
# import faiss
# import numpy as np
#
# # FAISS 인덱스 초기화 (L2 거리 기반 인덱스)
# dimension = 768  # 벡터 차원 수 (예: BERT 임베딩의 차원)
# index = faiss.IndexFlatL2(dimension)
#
#
# # 벡터 저장 함수
# def store_vectors_in_faiss(vectors: np.ndarray):
#     # FAISS는 2차원 배열을 요구하므로, 벡터 차원이 맞는지 확인
#     if len(vectors.shape) > 2:
#         # 불필요한 차원 제거 (예: (1, 1, 768) -> (1, 768))
#         vectors = np.squeeze(vectors)
#     # FAISS는 2차원 배열 형태의 벡터 입력을 요구함
#     if len(vectors.shape) != 2 or vectors.shape[1] != dimension:
#         raise ValueError(f"벡터의 차원이 올바르지 않습니다. 예상: 2D 배열 [{None}, {dimension}], 받은: {vectors.shape}")
#
#     # 벡터를 FAISS 인덱스에 추가
#     index.add(vectors)
#
# router = APIRouter()
# templates = Jinja2Templates(directory="app/templates")
#
# @router.get("/", response_class=HTMLResponse)
# async def root(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})
#
# @router.post("/search/", response_class=HTMLResponse)
# async def search_restaurant(request: Request, search_input: str = Form(...)):
#     # 입력된 검색어에서 지역과 키워드 추출
#     search_tokens = search_input.split()
#     if len(search_tokens) < 2:
#         raise HTTPException(status_code=400, detail="검색어와 지역을 모두 입력하세요.")
#
#     region = search_tokens[0]  # 첫 번째 단어를 지역으로 간주
#     query = ' '.join(search_tokens[1:])  # 나머지 단어를 검색어로 간주
#
#     # 키워드 추출
#     keywords = extract_keywords(query)
#
#     # 네이버 블로그 및 구글 맛집 데이터 가져오기
#     naver_results = fetch_naver_blog_data(query, region, keywords)
#     google_results = fetch_top_restaurants_nearby(query, region)
#
#     combined_results = naver_results + google_results
#
#     # 임베딩 벡터 생성 (결과에 대한 임베딩 처리)
#     embeddings = np.array([get_embedding(result.title + " " + result.description) for result in combined_results], dtype='float32')
#
#     # 불필요한 차원이 있으면 제거 (예: (1, 1, 768)을 (1, 768)으로 변환)
#     embeddings = np.squeeze(embeddings, axis=0)
#
#     # FAISS는 2차원 배열을 요구하므로, 임베딩을 확인 후 저장
#     store_vectors_in_faiss(embeddings)
#
#     # 검색 결과 반환
#     return templates.TemplateResponse("index.html", {
#         "request": request,
#         "search_results": combined_results
#     })