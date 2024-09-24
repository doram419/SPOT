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
def get_openai_embedding(text): 
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

    review_text = str()
    for text in data.reviews:
        review_text = review_text + text['text']
    
    # 숫자로 전환 되지 않은 것들만 벡터화
    embedding = {"name":get_openai_embedding(data.title),
         "address":get_openai_embedding(data.address),
         "reviews":get_openai_embedding(review_text),
         "description":get_openai_embedding(data.description),
         "rating":data.rating,
         "views":data.views,
         "price_level":data.price_level,
         "serves_beer":data.serves_beer,
         "serves_wine":data.serves_wine,
         "serves_breakfast":data.serves_breakfast,
         "serves_brunch":data.serves_brunch,
         "serves_lunch":data.serves_lunch,
         "serves_dinner":data.serves_dinner,
         "serves_vegetarian_food":data.serves_vegetarian_food,
         "takeout":data.takeout
         }
    
    metadata = {
        "name": data.title,
        "pk": fk,
        "link":data.link,
        "google_id":data.google_id
    }
    vector_store.add_to_index(embedding, metadata)

def searchVDB(query : str = "검색할 문장",
              search_amount : int = "결과를 몇 개 가져올지"): 
    """
    vector DB에서 검색해오는 함수

    반환 값 
    - list<dict>
    """
    query_embedding = get_openai_embedding(query)
    D, I = vector_store.index.search(np.array([query_embedding], dtype=np.float32), search_amount)
    results = []

    for idx, i in enumerate(I[0]):
        # vector_store.metadata는 리스트 타입
        if i < len(vector_store.metadata):
            # 리스트에서 직접 접근, meta는 dict 타입
            meta = vector_store.metadata[i]         
            # 찾아온 데이터를 result에 붙히기
            results.append({
                "title": meta.get("name", "Unknown"),
                "similarity": float(D[0][idx]),
                "pk": meta.get("pk", "Unknown"),
                "link": meta.get("link", "Unknown"),
                "google_id": meta.get("google_id", "Unknown")
            })
    
    # 유사도 순으로 정렬
    results.sort(key=lambda x: x["similarity"])
    return results
