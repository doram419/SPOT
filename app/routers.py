from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .vectorRouter.FaissVectorStore import FaissVectorStore
from .vectorRouter.vectorMgr import get_openai_embedding
from app.promptMgr import summarize_desc
import numpy as np
from rank_bm25 import BM25Okapi


# FastAPI의 APIRouter 인스턴스 생성
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# FAISS 벡터 스토어 초기화
vector_store = FaissVectorStore()

# BM25 모델 초기화 (vector_store에 있는 문서들의 텍스트 사용)
corpus = [meta.get("summary", "") for meta in vector_store.metadata]
tokenized_corpus = [doc.split(" ") for doc in corpus]
bm25 = BM25Okapi(tokenized_corpus)

# GET 요청 처리, 메인 페이지 렌더링
@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

# POST 요청을 통해 검색을 처리하는 엔드포인트에 하이브리드 검색 추가
@router.post("/search/", response_class=HTMLResponse)
async def search_restaurant(request: Request, search_input: str = Form(...)):
    if not search_input:
        raise HTTPException(status_code=400, detail="검색어를 입력하세요.")

    print(f"검색어: {search_input}")

    # 1. BM25 검색을 먼저 수행 (텍스트 기반 검색)
    tokenized_query = search_input.split(" ")
    bm25_scores = bm25.get_scores(tokenized_query)  # BM25 점수 계산
    top_bm25_indices = np.argsort(bm25_scores)[-10:]  # 상위 10개의 문서 인덱스 선택

    if len(top_bm25_indices) == 0:
        raise HTTPException(status_code=404, detail="검색 결과가 없습니다.")

    # 2. 검색어에 대한 임베딩 생성 (OpenAI 사용)
    embedding = get_openai_embedding(search_input)
    if vector_store.dim is None:
        print("경고: 벡터 저장소가 비어 있습니다. 먼저 데이터를 추가해주세요.")
        raise HTTPException(status_code=500, detail="벡터 저장소에 데이터가 없습니다.")

    # embedding 차원 맞추기
    if embedding.ndim == 1:
        padding = np.zeros(max(0, vector_store.dim - len(embedding)), dtype=np.float32)
        embedding = np.concatenate([embedding, padding])
    elif embedding.ndim == 2:
        if embedding.shape[0] == 1:
            embedding = embedding.flatten()  # 1차원 배열로 변환
        else:
            raise ValueError("Unexpected embedding shape")
    else:
        raise ValueError("예상치 못한 임베딩 차원입니다.")

    print(f"임베딩 벡터: {embedding}")
    print(f"임베딩 벡터 차원: {embedding.shape}")
    
    # embedding을 2차원 배열로 변환 (FAISS 검색에 맞게)
    embedding = embedding.reshape(1, -1)

    # 3. FAISS 벡터 검색 수행 (BM25로 필터링된 상위 문서들에 대해 검색)
    D, I = vector_store.index.search(embedding, k=10)  # FAISS 인덱스에서 검색

    # 4. FAISS 결과와 BM25 결과를 결합하여 최종 상위 결과 선택
    final_ranked_indices = list(set(top_bm25_indices).intersection(set(I[0])))  # BM25와 FAISS의 교집합을 사용

    if not final_ranked_indices:
        final_ranked_indices = top_bm25_indices[:5]  # 교집합이 없으면 BM25의 상위 5개 문서 사용

    # 5. 결과를 사용자의 검색어와 맞는 형태로 요약 및 출력
    results = []
    for idx, i in enumerate(final_ranked_indices):
        if i < len(vector_store.metadata):
            meta = vector_store.metadata[i]
            summary = summarize_desc(meta.get("title", "Unknown"), meta.get("summary", ""))
            results.append({
                "title": meta.get("title", "Unknown"),
                "similarity": float(D[0][idx]),
                "chunked_desc": meta.get("desc", "Unknown"),
                "summary": summary,
                "link": meta.get("link", "https://none")
            })


    print(f"검색된 거리(D): {D}")
    print(f"검색된 인덱스(I): {I}")

    # 검색 결과 페이지 렌더링
    return templates.TemplateResponse("results.html", {
        "request": request,
        "results": results,
        "search_input": search_input
    })
