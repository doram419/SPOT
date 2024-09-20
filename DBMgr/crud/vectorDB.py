import os
from FaissVectorStore import FaissVectorStore
import numpy as np
from dotenv import load_dotenv
from models import SearchResult
from langchain_openai import OpenAIEmbeddings

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
    embedding = get_openai_embedding(data.description)
    metadata = {
        "name": data.title,
        "pk": fk
    }
    vector_store.add_to_index(embedding, metadata)

def searchVDB(query : str = "검색할 문장",
              search_amount : int = "결과를 몇 개 가져올지"):
    """
    vector DB에서 검색해오는 함수
    """
    query_embedding = get_openai_embedding(query)
    D, I = vector_store.index.search(np.array([query_embedding], dtype=np.float32), search_amount)

    results = []
    for idx, i in enumerate(I[0]):
        if i < len(vector_store.metadata):
            metadata = vector_store.metadata[i]  # 리스트에서 직접 접근
            if isinstance(metadata, dict):  # metadata가 딕셔너리인 경우
                results.append({
                    "title": metadata.get("name", "Unknown"),
                    "similarity": float(D[0][idx]),
                    "pk": metadata.get("pk", "Unknown")
                })
            elif isinstance(metadata, list) and len(metadata) > 0:  # metadata가 리스트인 경우
                metadata_dict = metadata[0] if isinstance(metadata[0], dict) else {}
                results.append({
                    "title": metadata_dict.get("name", "Unknown"),
                    "similarity": float(D[0][idx]),
                    "pk": metadata_dict.get("pk", "Unknown")
                })
    
    results.sort(key=lambda x: x["similarity"])
    return results

if __name__ == "__main__":
    sample_data1 = SearchResult(
        title="A 레스토랑",
        link="https://A.com",
        description="해산물 요리, 회, 수산물, 파티하기 좋은 시끌벅적한 단체 장소",
        rating=0.0,
        views=10000
    )

    sample_data2 = SearchResult(
        title="B 레스토랑",
        link="https://B.com",
        description="비건 메뉴, 파스타, 피자 등의 양식을 파는 데이트 하기 좋은 조용한 장소",
        rating=0.0,
        views=10000
    )

    sample_data3 = SearchResult(
        title="C 레스토랑",
        link="https://B.com",
        description="아시안 레스토랑, 야시장 분위기가 물씬 나는, 특이한, 이색적인 장소",
        rating=0.0,
        views=10000
    )
    # TODO:description chunking
    # saveToVDB(sample_data3, 3)

    result = searchVDB("해산물", 1)
    print(result[0]['title'])
    # print(result)