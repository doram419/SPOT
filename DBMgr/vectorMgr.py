import os
from vectorStore.FaissVectorStore import FaissVectorStore
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings  # 새로운 모듈에서 임포트
import numpy as np
from crawling.datas.data import Data

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
    OpenAI를 통해 자연어 임베딩을 생성하는 함수
    :param text: 임베딩 할 텍스트
    :return: 임베딩 벡터
    """
    embedding = embeddings.embed_query(text)
    return np.array(embedding, dtype=np.float32)

def saveToVDB(data: Data):
    """
    data로 받은 객체를 VectorDB에 저장하는 함수
    :param data: 저장할 객체
    """
    
    # 숫자로 전환 되지 않은 것들만 벡터화
    vectorization_desc = {}
    for i, des in enumerate(data.desc):
        vectorization_desc[i] = get_openai_embedding(des)  # 인덱스를 키로 사용
    
    metadata = {
        "title": data.title,
        "desc": data.desc,
        "summary": data.summary
    }
    
    # 벡터와 메타데이터를 함께 저장
    vector_store.add_to_index(vectorization_desc, metadata)
    vector_store.save_index()

if __name__ == "__main__":
    d = Data("제목", ["아", "무"], ["거", "나"])
    saveToVDB(d)
