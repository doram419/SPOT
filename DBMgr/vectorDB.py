import os
from FaissVectorStore import FaissVectorStore
import numpy as np
from dotenv import load_dotenv
from models import SearchResult
from langchain.embeddings import OpenAIEmbeddings


# .env 파일에서 API 키 로드 (환경 변수 설정)
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 임베딩 객체 생성
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-3-small")

# Faiss 벡터 스토어 인스턴스 생성
vector_store = FaissVectorStore()

# 텍스트 임베딩 함수
def get_openai_embedding(text : str = "임베딩 할 자연어"): 
    """
    openai를 통해서 자연어 임베딩을 해서 돌려주는 함수
    """
    return embeddings.embed_query(text)

def saveToVDB(data : SearchResult = "저장할 데이터",
              fk : int = "rdb에 저장된 키 값"):
    """
    SearchResult를 주면 vectorDB에 크롤링한 데이터를 저장하는 함수
    rdb와 연동을 위해 fk 필수

    저장하는 데이터
    - 가게명 
    - 설명
    - rdb의 pk : 파라미터 fk
    """
    print(fk)
    # TODO:description chunking
    embedding = get_openai_embedding(data.description)
    metadata = {
        "name": data.title,
        "pk": fk
    }
    vector_store.add_to_index(embedding, metadata)
    vector_store.save_index()


def searchVDB(query: str = "검색할 문장", search_amount: int = "결과를 몇 개 가져올지"):
    query_embedding = get_openai_embedding(query)
    print(f"검색 쿼리 임베딩: {query_embedding}")
    D, I = vector_store.index.search(np.array([query_embedding], dtype=np.float32), search_amount)
    results = []

    for idx, i in enumerate(I[0]):
        if i < len(vector_store.metadata):
            meta = vector_store.metadata[i]
            print(f"검색 결과: {meta}")
            results.append({
                "title": meta.get("name", "Unknown"),
                "similarity": float(D[0][idx]),
                "pk": meta.get("pk", "Unknown")
            })

    # 유사도 순으로 정렬
    results.sort(key=lambda x: x["similarity"])
    return results
