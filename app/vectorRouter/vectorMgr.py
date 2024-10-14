import re
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from rank_bm25 import BM25Okapi
import os
import numpy as np
from collections import defaultdict
from .improved_faiss_vector_store import ImprovedFaissVectorStore
from .promptMgr import generate_gpt_response
from .exceptions import (
    EmptySearchQueryException,
    NoSearchResultsException,
    EmptyVectorStoreException
)

# .env 파일에서 API 키 로드
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 임베딩 객체 생성
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vector_store = ImprovedFaissVectorStore(index_dir="app/vdb")

# 코퍼스 생성
async def get_corpus():
    all_metadata = []
    for shard_metadata in vector_store.metadata:
        all_metadata.extend(shard_metadata)
    corpus = [meta.get("chunk_content", " ") for meta in all_metadata]
    if not corpus:
        print("경고: 코퍼스가 비어 있습니다.")
    return corpus

# BM25 모델 초기화
async def initialize_bm25():
    corpus = await get_corpus()
    if not corpus:
        raise ValueError("코퍼스가 비어 있어 BM25 모델을 초기화할 수 없습니다.")
    tokenized_corpus = [doc.split(" ") for doc in corpus if doc.strip()]
    if not tokenized_corpus:
        raise ValueError("토큰화된 코퍼스가 비어 있습니다.")
    print(f"토큰화된 코퍼스 크기: {len(tokenized_corpus)}")
    return BM25Okapi(tokenized_corpus)

# OpenAI 임베딩을 생성하는 함수
def get_openai_embedding(text: str):
    embedding = embeddings.embed_query(text)
    return np.array(embedding, dtype=np.float32)

# 검색어를 전처리하는 함수
def preprocess_search_input(search_input: str):
    keywords = re.findall(r'\b\w+\b', search_input)
    keywords = [word for word in keywords if len(word) > 1]
    return keywords

# RAG(검색 + 생성) 기반 검색 함수
async def search_with_rag(search_input: str, k: int = 5, bm25_weight: float = 0.6, faiss_weight: float = 0.4):
    if not search_input:
        raise EmptySearchQueryException()

    # 1. 검색어 전처리
    keywords = preprocess_search_input(search_input)
   
    # 2. BM25 검색
    try:
        bm25 = await initialize_bm25()
        corpus = await get_corpus()
        bm25_scores = np.zeros(len(corpus))
        for keyword in keywords:
            tokenized_query = keyword.split(" ")
            keyword_scores = bm25.get_scores(tokenized_query)
            bm25_scores += keyword_scores

        # BM25 점수 정규화
        bm25_max = np.max(bm25_scores)
        if bm25_max > 0:
            bm25_scores = bm25_scores / bm25_max
        else:
            print("경고: 모든 BM25 점수가 0입니다.")
            bm25_scores = np.zeros_like(bm25_scores)

        # 상위 BM25 인덱스 선택
        top_bm25_indices = np.argsort(bm25_scores)[-200:]
        print(f"BM25 후보 개수: {len(top_bm25_indices)}")

        if len(top_bm25_indices) == 0:
            raise NoSearchResultsException()
    except Exception as e:
        print(f"BM25 검색 중 오류 발생: {str(e)}")
        raise
    
    try:
        # 3. FAISS 검색
        embedding = get_openai_embedding(search_input)
        
        if vector_store.dim is None:
            raise EmptyVectorStoreException()
        
        D, I = await vector_store.search(embedding.reshape(1, -1), k=200)
        
        if D.size == 0 or I.size == 0:
            print("FAISS search returned empty results")
            raise NoSearchResultsException()

        # D와 I는 이미 1D 배열이므로 그대로 사용
        distances = D
        indices = I
        
        print(f"FAISS 후보 개수: {len(indices)}")

        # FAISS 유사도 정규화 (거리를 유사도로 변환)
        faiss_similarities = 1 / (1 + distances)
        faiss_max = np.max(faiss_similarities) if faiss_similarities.size > 0 else 0
        if faiss_max > 0:
            faiss_similarities = faiss_similarities / faiss_max
        else:
            print("Warning: All FAISS similarities are zero")
            faiss_similarities = np.zeros_like(faiss_similarities)
        
        print(f"FAISS similarities shape: {faiss_similarities.shape}")
    except Exception as e:
        print(f"FAISS 검색 중 예상치 못한 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

    # 5. BM25와 FAISS 점수 결합
    combined_scores = {}

    for idx in top_bm25_indices:
        combined_scores[idx] = bm25_scores[idx] * bm25_weight

    for idx, doc_id in enumerate(I):
        if doc_id in combined_scores:
            combined_scores[doc_id] += faiss_similarities[idx] * faiss_weight
        else:
            combined_scores[doc_id] = faiss_similarities[idx] * faiss_weight

    # 6. 결합된 점수로 상위 문서 선택 및 정렬
    ranked_indices = sorted(combined_scores, key=combined_scores.get, reverse=True)
    print(f"결합된 후보 개수: {len(ranked_indices)}")

    # 7. 결과 수집 및 같은 data_id를 가진 chunk 결합
    seen = set()
    combined_results = defaultdict(list)

    all_metadata = []
    for shard_metadata in vector_store.metadata:
        all_metadata.extend(shard_metadata)

    for idx in ranked_indices:
        if idx < len(all_metadata):
            meta = all_metadata[idx]
            data_id = meta.get("data_id")

            if data_id in seen:
                continue
            seen.add(data_id)

            for m in all_metadata:
                if m.get("data_id") == data_id:
                    chunk_content = m.get("chunk_content", "")
                    if chunk_content:
                        combined_results[data_id].append(chunk_content)

            if len(combined_results) >= k:
                break

    print(f"선택된 결과 수: {len(combined_results)}")

    if len(combined_results) < k:
        print("경고: 검색 결과가 충분하지 않습니다. 데이터 양을 확인하세요.")

    # 8. 결합된 내용으로 요약 생성
    selected_results = []
    unique_names = set()
    for data_id, chunks in combined_results.items():
        full_content = " ".join(chunks)

        link = ""
        for m in all_metadata:
            if m.get("data_id") == data_id:
                temp_link = m.get("link", "")
                if temp_link and temp_link.lower() != "none":
                    link = temp_link
                    break

        meta = next((m for m in all_metadata if m.get("data_id") == data_id), None)
        if meta is None:
            continue
        name = meta.get("name", "Unknown")
        address = meta.get("address", "Unknown")

        if name in unique_names:
            continue
        unique_names.add(name)

        print(f"선택된 링크: {link}")

        # 요약 생성
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

