import re
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from rank_bm25 import BM25Okapi
import os
import numpy as np
from collections import defaultdict
from .FaissVectorStore import FaissVectorStore
from .promptMgr import generate_gpt_response
from .exceptions import (
    EmptySearchQueryException,
    NoSearchResultsException,
    EmptyVectorStoreException,
    VectorSearchException,
)
from .threshold import filter_results
import matplotlib.pyplot as plt

# 실행 시작 로그
print("vectorMgr.py 실행 시작")

# .env 파일에서 API 키 로드
print(".env 파일에서 API 키 로드 시도 중...")
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    print("API 키 로드 성공")
else:
    print("경고: API 키를 로드하지 못했습니다")

# OpenAI 임베딩 객체 생성
try:
    print("OpenAI 임베딩 객체 생성 중...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    print("OpenAI 임베딩 객체 생성 완료")
except Exception as e:
    print(f"임베딩 객체 생성 중 오류 발생: {e}")

# 벡터 저장소 인스턴스 생성
try:
    print("벡터 저장소 인스턴스 생성 중...")
    vector_store = FaissVectorStore()
    print("벡터 저장소 인스턴스 생성 완료")
except Exception as e:
    print(f"벡터 저장소 생성 중 오류 발생: {e}")

# 코퍼스 생성
print("코퍼스 생성 중...")
corpus = [meta.get("summary", " ") for meta in vector_store.metadata]
print(f"코퍼스 생성 완료, 총 {len(corpus)}개의 문서")

# 코퍼스가 비어 있는 경우 예외 발생
if not corpus:
    raise EmptyVectorStoreException("메타 데이터 안에 summary가 없습니다.")

# BM25 모델 초기화
print("BM25 모델 초기화 중...")
tokenized_corpus = [doc.split(" ") for doc in corpus]
bm25 = BM25Okapi(tokenized_corpus)
print("BM25 모델 초기화 완료")

# OpenAI 임베딩을 생성하는 함수
def get_openai_embedding(text: str):
    print(f"OpenAI 임베딩 생성 중... 입력 텍스트: {text}")
    embedding = embeddings.embed_query(text)
    print("OpenAI 임베딩 생성 완료")
    return np.array(embedding, dtype=np.float32)

# 검색어를 전처리하는 함수
def preprocess_search_input(search_input: str):
    print(f"검색어 전처리 중... 입력 검색어: {search_input}")
    keywords = re.findall(r'\b\w+\b', search_input)
    keywords = [word for word in keywords if len(word) > 1]
    print(f"검색어 전처리 완료, 키워드: {keywords}")
    return keywords

# RAG(검색 + 생성) 기반 검색 함수
def search_with_rag(search_input: str, k: int = 5, bm25_weight: float = 0.6, faiss_weight: float = 0.4):
    print("RAG 검색 함수 호출")
    
    if not search_input:
        raise EmptySearchQueryException()

    # 1. 검색어 전처리
    keywords = preprocess_search_input(search_input)

    # 2. BM25 검색
    print("BM25 검색 시작")
    bm25_scores = np.zeros(len(corpus))
    for keyword in keywords:
        tokenized_query = keyword.split(" ")
        keyword_scores = bm25.get_scores(tokenized_query)
        bm25_scores += keyword_scores

    # BM25 점수 정규화
    if np.max(bm25_scores) > 0:
        bm25_scores = bm25_scores / np.max(bm25_scores)
    print("BM25 검색 완료")

    # 상위 BM25 인덱스 선택
    top_bm25_indices = np.argsort(bm25_scores)[-200:]
    print(f"BM25 후보 개수: {len(top_bm25_indices)}")

    if len(top_bm25_indices) == 0:
        raise NoSearchResultsException()

    # 3. FAISS 검색
    print("FAISS 검색 시작")
    embedding = get_openai_embedding(search_input)
    
    if vector_store.dim is None:
        raise EmptyVectorStoreException()

    D, I = vector_store.search(embedding.reshape(1, -1), k=200)
    print(f"FAISS 후보 개수: {len(I[0])}")

    # 거리 값의 분포를 시각화하기 위해 히스토그램을 출력
    plt.hist(D[0], bins=20)
    plt.xlabel('Distance')
    plt.ylabel('Frequency')
    plt.title('Distribution of FAISS Distances')
    plt.show(block=False)

    # 동적으로 쓰레스홀드 설정
    threshold = np.percentile(D[0], 75)
    print(f"쓰레스홀드 적용 전 거리 개수: {len(D[0])}")
    print(f"쓰레스홀드 적용 전 거리 값 (일부): {D[0][:5]}")

    # 쓰레스홀드 필터링 적용
    filtered_distances, filtered_indices = filter_results(D[0], I[0], threshold)
    print(f"쓰레스홀드 적용 후 거리 개수: {len(filtered_distances)}")
    print(f"쓰레스홀드 적용 후 거리 값 (일부): {filtered_distances[:5]}")
    print(f"쓰레스홀드 적용 후 인덱스 값 (일부): {filtered_indices[:5]}")

    # FAISS 유사도 정규화
    print("FAISS 유사도 정규화 중...")
    faiss_similarities = 1 - filtered_distances
    if np.max(faiss_similarities) > 0:
        faiss_similarities = faiss_similarities / np.max(faiss_similarities)
    print(f"FAISS 유사도 정규화 완료 (일부): {faiss_similarities[:5]}")

    # 5. BM25와 FAISS 점수 결합
    print("BM25와 FAISS 점수 결합 시작")
    combined_scores = {}

    # BM25 점수 결합
    for idx in top_bm25_indices:
        combined_scores[idx] = bm25_scores[idx] * bm25_weight

    for idx, doc_id in enumerate(filtered_indices):
        if doc_id in combined_scores:
            combined_scores[doc_id] += faiss_similarities[idx] * faiss_weight
        else:
            combined_scores[doc_id] = faiss_similarities[idx] * faiss_weight

    ranked_indices = sorted(combined_scores, key=combined_scores.get, reverse=True)
    print(f"결합된 후보 개수: {len(ranked_indices)}")

    # 7. 결과 수집 및 같은 data_id를 가진 chunk 결합
    seen = set()
    combined_results = defaultdict(list)

    for idx in ranked_indices:
        if idx < len(vector_store.metadata):
            meta = vector_store.metadata[idx]
            data_id = meta.get("data_id")

            if data_id in seen:
                continue
            seen.add(data_id)

            for m in vector_store.metadata:
                if m.get("data_id") == data_id:
                    chunk_content = m.get("chunk_content", "")
                    if chunk_content:
                        combined_results[data_id].append(chunk_content)

            if len(combined_results) >= k:
                break

    print(f"선택된 결과 수: {len(combined_results)}")

    if len(combined_results) < k:
        print("경고: 검색 결과가 충분하지 않습니다. 데이터 양을 확인하세요.")

    selected_results = []
    unique_names = set()
    for data_id, chunks in combined_results.items():
        full_content = " ".join(chunks)
        link = ""
        for m in vector_store.metadata:
            if m.get("data_id") == data_id:
                temp_link = m.get("link", "")
                if temp_link and temp_link.lower() != "none":
                    link = temp_link
                    break

        meta = next(m for m in vector_store.metadata if m.get("data_id") == data_id)
        name = meta.get("name", "Unknown")
        address = meta.get("address", "Unknown")

        if name in unique_names:
            continue
        unique_names.add(name)

        print(f"선택된 링크: {link}")

        summary = generate_gpt_response(name, full_content)
        selected_results.append({
            "name": name,
            "summary": summary,
            "address": address,
            "data_id": data_id,
            "link": link
        })

    return {
        "generated_response": "검색 결과 요약 생성 완료",
        "results": selected_results
    }

# main 블록 추가
if __name__ == "__main__":
    print("코드 실행 시작")
    # 테스트 호출 - 검색어를 넣어 함수 호출 등
    try:
        result = search_with_rag("가족들이랑 국밥", k=5)
        print("검색 결과:", result)
    except Exception as e:
        print(f"검색 실행 중 오류 발생: {e}")
