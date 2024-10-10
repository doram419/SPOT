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
# OpenAI 임베딩 객체를 API 키와 임베딩 모델("text-embedding-3-small")을 사용해 초기화합니다.
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-3-small")

# 벡터 저장소 인스턴스 생성
# 벡터 검색을 위한 Faiss 기반 벡터 저장소 인스턴스를 생성합니다.
vector_store = FaissVectorStore()

# 코퍼스 생성
# 벡터 저장소 메타 데이터에서 'summary' 값을 추출하여 코퍼스를 만듭니다. 
# 'summary' 값이 없는 경우 빈 문자열을 사용합니다.
corpus = [meta.get("summary", " ") for meta in vector_store.metadata]

# 코퍼스가 비어 있는 경우 예외를 발생시킵니다.
if not corpus:
    raise EmptyVectorStoreException("메타 데이터 안에 summary가 없습니다.")

# BM25 모델 초기화
# 코퍼스의 각 문서를 공백을 기준으로 토큰화한 후, BM25 모델을 초기화합니다.
tokenized_corpus = [doc.split(" ") for doc in corpus]
bm25 = BM25Okapi(tokenized_corpus)

# OpenAI 임베딩을 생성하는 함수
def get_openai_embedding(text: str):
    # OpenAI 임베딩을 사용하여 주어진 텍스트의 임베딩을 생성한 후, float32 타입의 NumPy 배열로 변환합니다.
    embedding = embeddings.embed_query(text)
    return np.array(embedding, dtype=np.float32)

# 검색어를 전처리하는 함수
def preprocess_search_input(search_input: str):
    # 검색 입력에서 단어를 추출합니다(길이가 1 이하인 단어는 필터링합니다).
    keywords = re.findall(r'\b\w+\b', search_input)
    keywords = [word for word in keywords if len(word) > 1]
    return keywords

# RAG(검색 + 생성) 기반 검색 함수
def search_with_rag(search_input: str, k: int = 5, bm25_weight: float = 0.5, faiss_weight: float = 0.5):
    # 검색 입력이 비어 있으면 예외를 발생시킵니다.
    if not search_input:
        raise EmptySearchQueryException()

    # 1. 검색어 전처리
    # 검색어에서 키워드를 추출하고 전처리합니다.
    keywords = preprocess_search_input(search_input)

    # 2. BM25 검색
    # BM25 알고리즘을 사용해 코퍼스의 각 문서에 대해 검색 점수를 계산합니다.
    bm25_scores = np.zeros(len(corpus))
    for keyword in keywords:
        tokenized_query = keyword.split(" ")
        keyword_scores = bm25.get_scores(tokenized_query)
        bm25_scores += keyword_scores

    # BM25 점수 정규화
    # BM25 점수가 0 이상이면, 점수를 0~1 사이의 범위로 정규화합니다.
    if np.max(bm25_scores) > 0:
        bm25_scores = bm25_scores / np.max(bm25_scores)

    # 상위 BM25 인덱스 선택
    # BM25 검색 결과 중 상위 200개의 후보 문서를 선택합니다.
    top_bm25_indices = np.argsort(bm25_scores)[-200:]  # 후보 수 증가
    print(f"BM25 후보 개수: {len(top_bm25_indices)}")

    # 검색 결과가 없으면 예외를 발생시킵니다.
    if len(top_bm25_indices) == 0:
        raise NoSearchResultsException()

    # 3. FAISS 검색
    # OpenAI 임베딩을 사용해 검색 입력에 대한 벡터를 생성합니다.
    embedding = get_openai_embedding(search_input)
    
    # 벡터 저장소의 차원 정보가 없으면 예외를 발생시킵니다.
    if vector_store.dim is None:
        raise EmptyVectorStoreException()

    # 생성된 벡터를 사용해 FAISS 검색을 수행하여 상위 200개의 후보 문서를 검색합니다.
    D, I = vector_store.search(embedding.reshape(1, -1), k=200)  # 후보 수 증가
    print(f"FAISS 후보 개수: {len(I[0])}")

    # FAISS 유사도 정규화
    # FAISS에서 검색된 결과의 유사도를 0~1 사이로 정규화합니다.
    faiss_similarities = 1 - D[0]
    if np.max(faiss_similarities) > 0:
        faiss_similarities = faiss_similarities / np.max(faiss_similarities)

    # 5. BM25와 FAISS 점수 결합
    # BM25와 FAISS 점수를 결합하여 최종 점수를 계산합니다.
    combined_scores = {}

    # BM25 결과에서 상위 문서들의 점수를 결합합니다.
    for idx in top_bm25_indices:
        combined_scores[idx] = bm25_scores[idx] * bm25_weight

    # FAISS 결과에서 상위 문서들의 점수를 결합합니다.
    for idx, doc_id in enumerate(I[0]):
        if doc_id in combined_scores:
            combined_scores[doc_id] += faiss_similarities[idx] * faiss_weight
        else:
            combined_scores[doc_id] = faiss_similarities[idx] * faiss_weight

    # 6. 결합된 점수로 상위 문서 선택 및 정렬
    # 결합된 점수를 기준으로 상위 문서들의 인덱스를 내림차순으로 정렬합니다.
    ranked_indices = sorted(combined_scores, key=combined_scores.get, reverse=True)
    print(f"결합된 후보 개수: {len(ranked_indices)}")

    # 7. 결과 수집
    # 중복된 문서를 제거하고 상위 k개의 검색 결과를 선택합니다.
    seen = set()
    selected_results = []
    for idx in ranked_indices:
        if idx < len(vector_store.metadata):
            meta = vector_store.metadata[idx]

            # 링크를 기준으로 중복을 확인하고 중복된 항목은 건너뜁니다.
            unique_key = meta.get("link"), meta.get("name")
            if unique_key in seen:
                continue
            seen.add(unique_key)

            # 선택된 문서의 메타 데이터를 결과 리스트에 추가합니다.
            selected_results.append({
                "name": meta.get("name", "Unknown"),
                "chunk_content": meta.get("chunk_content", ""),
                "address": meta.get("address", "Unknown"),
                "link": meta.get("link", "https://none")
            })

            # 상위 k개의 결과만 선택합니다.
            if len(selected_results) >= k:
                break

    print(f"선택된 결과 수: {len(selected_results)}")

    # 검색 결과가 k개보다 적으면 경고 메시지를 출력합니다.
    if len(selected_results) < k:
        print("경고: 검색 결과가 충분하지 않습니다. 데이터 양을 확인하세요.")

    # 8. 응답 생성
    # 선택된 검색 결과를 GPT 모델을 사용해 하나의 응답으로 생성합니다.
    concatenated_summaries = "\n\n".join([f"{result['name']}: {result['chunk_content']}" for result in selected_results])
    response = generate_gpt_response("검색 결과", concatenated_summaries)

    return {
        "generated_response": response,  # 생성된 응답
        "search_results": selected_results  # 선택된 검색 결과
    }
