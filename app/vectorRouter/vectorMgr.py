import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings  # 새로운 모듈에서 임포트
import numpy as np
from .FaissVectorStore import FaissVectorStore
from .promptMgr import summarize_desc

# .env 파일에서 API 키 로드 (환경 변수 설정)
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 임베딩 객체 생성
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-3-small")

# 벡터 저장소 인스턴스 생성
vector_store = FaissVectorStore()

# 텍스트 임베딩 함수
def get_openai_embedding(text: str): 
    """
    OpenAI를 통해 자연어 임베딩을 생성하는 함수
    :param text: 임베딩 할 텍스트
    :return: 임베딩 벡터
    """
    embedding = embeddings.embed_query(text)
    return np.array(embedding, dtype=np.float32)

# 서치 함수
def search(search_input: str, k: int = 5):
    """
    주어진 검색어에 대해 유사한 항목을 검색하는 함수
    :param search_input: 검색어
    :param k: 반환할 결과의 수
    :return: 검색 결과 리스트
    """
    if not search_input:
        raise ValueError("검색어를 입력하세요.")

    embedding = get_openai_embedding(search_input)

    if vector_store.dim is None:
        print("경고: 벡터 저장소가 비어 있습니다. 먼저 데이터를 추가해주세요.")
        return []

    # 임베딩 차원 조정
    if embedding.ndim == 1:
        padding = np.zeros(max(0, vector_store.dim - len(embedding)), dtype=np.float32)
        embedding = np.concatenate([embedding, padding])
    elif embedding.ndim == 2:
        if embedding.shape[0] == 1:
            embedding = embedding.flatten()
        else:
            raise ValueError("Unexpected embedding shape")
        padding = np.zeros(max(0, vector_store.dim - len(embedding)), dtype=np.float32)
        embedding = np.concatenate([embedding, padding])
    else:
        raise ValueError("예상치 못한 임베딩 차원입니다.")

    # 임베딩을 2차원 배열로 변환
    embedding = embedding.reshape(1, -1)

    D, I = vector_store.search(embedding, k=k)
    
    results = []
    for idx, i in enumerate(I[0]):
        if i < len(vector_store.metadata):
            meta = vector_store.metadata[i]
            summary = summarize_desc(meta.get("title", "Unknown"), meta.get("summary", ""))
            results.append({
                "title": meta.get("title", "Unknown"),
                "similarity": float(D[0][idx]),
                "summary": summary,
                "link": meta.get("link", "https://none")
            })

    return results