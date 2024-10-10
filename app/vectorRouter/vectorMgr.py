import re
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings 
from rank_bm25 import BM25Okapi
import os
import numpy as np
from .FaissVectorStore import FaissVectorStore
from .promptMgr import generate_gpt_response
from .exceptions import (
    EmptySearchQueryException,
    NoSearchResultsException,
    EmptyVectorStoreException,
    VectorSearchException,
)

# .env 파일에서 API 키 로드
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 임베딩 객체 생성
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-3-small")

# 벡터 저장소 인스턴스 생성
vector_store = FaissVectorStore()

# 코퍼스 생성
corpus = [meta.get("summary", " ") for meta in vector_store.metadata]

if not corpus:
    raise EmptyVectorStoreException("메타 데이터 안에 summary가 없습니다.")

# BM25 모델 초기화
tokenized_corpus = [doc.split(" ") for doc in corpus]
bm25 = BM25Okapi(tokenized_corpus)

def get_openai_embedding(text: str):
    embedding = embeddings.embed_query(text)
    return np.array(embedding, dtype=np.float32)

def preprocess_search_input(search_input: str):
    keywords = re.findall(r'\b\w+\b', search_input)
    keywords = [word for word in keywords if len(word) > 1]
    return keywords

def search_with_rag(search_input: str, k: int = 5, bm25_weight: float = 0.5, faiss_weight: float = 0.5):
    if not search_input:
        raise EmptySearchQueryException()

    # 1. 검색어 전처리
    keywords = preprocess_search_input(search_input)

    # 2. BM25 검색
    bm25_scores = np.zeros(len(corpus))
    for keyword in keywords:
        tokenized_query = keyword.split(" ")
        keyword_scores = bm25.get_scores(tokenized_query)
        bm25_scores += keyword_scores

    # BM25 점수 정규화
    if np.max(bm25_scores) > 0:
        bm25_scores = bm25_scores / np.max(bm25_scores)

    # 상위 BM25 인덱스 선택
    top_bm25_indices = np.argsort(bm25_scores)[-200:]  # 후보 수 증가
    print(f"BM25 후보 개수: {len(top_bm25_indices)}")

    if len(top_bm25_indices) == 0:
        raise NoSearchResultsException()

    # 3. FAISS 검색
    embedding = get_openai_embedding(search_input)
    if vector_store.dim is None:
        raise EmptyVectorStoreException()

    D, I = vector_store.search(embedding.reshape(1, -1), k=200)  # 후보 수 증가
    print(f"FAISS 후보 개수: {len(I[0])}")

    # FAISS 유사도 정규화
    faiss_similarities = 1 - D[0]
    if np.max(faiss_similarities) > 0:
        faiss_similarities = faiss_similarities / np.max(faiss_similarities)

    # 5. BM25와 FAISS 점수 결합
    combined_scores = {}

    # BM25 결과
    for idx in top_bm25_indices:
        combined_scores[idx] = bm25_scores[idx] * bm25_weight

    # FAISS 결과
    for idx, doc_id in enumerate(I[0]):
        if doc_id in combined_scores:
            combined_scores[doc_id] += faiss_similarities[idx] * faiss_weight
        else:
            combined_scores[doc_id] = faiss_similarities[idx] * faiss_weight

    # 6. 결합된 점수로 상위 문서 선택 및 정렬
    ranked_indices = sorted(combined_scores, key=combined_scores.get, reverse=True)
    print(f"결합된 후보 개수: {len(ranked_indices)}")

    # 7. 결과 수집
    seen = set()
    selected_results = []
    for idx in ranked_indices:
        if idx < len(vector_store.metadata):
            meta = vector_store.metadata[idx]

            unique_key = meta.get("link","name")  # 링크(URL)를 기준으로 중복 제거
            if unique_key in seen:
                continue  # 중복된 항목은 건너뜀
            seen.add(unique_key)

            selected_results.append({
                "name": meta.get("name", "Unknown"),
                "summary": meta.get("summary", ""),
                "address": meta.get("address", "Unknown"),
                "link": meta.get("link", "https://none")
            })

            if len(selected_results) >= k:
                break

    print(f"선택된 결과 수: {len(selected_results)}")

    if len(selected_results) < k:
        print("경고: 검색 결과가 충분하지 않습니다. 데이터 양을 확인하세요.")

    # 8. 응답 생성
    concatenated_summaries = "\n\n".join([f"{result['name']}: {result['summary']}" for result in selected_results])
    response = generate_gpt_response("검색 결과", concatenated_summaries)

    return {
        "generated_response": response,
        "search_results": selected_results
    }
