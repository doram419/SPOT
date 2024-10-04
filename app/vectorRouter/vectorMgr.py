import os
import pickle
import numpy as np
import faiss
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from .promptMgr import summarize_desc
from .exceptions import EmptySearchQueryException, NoSearchResultsException, EmptyVectorStoreException

# .env 파일에서 API 키 로드 (환경 변수 설정)
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 임베딩 객체 생성
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-3-small")

# 벡터 저장소 클래스 정의
class FaissVectorStore:
    def __init__(self, index_file: str, metadata_file: str):
        # FAISS 인덱스 로드
        if os.path.exists(index_file):
            self.index = faiss.read_index(index_file)
            self.dim = self.index.d
            print(f"FAISS 인덱스 로드 완료. 차원: {self.dim}")  # FAISS 인덱스 로드 확인
        else:
            raise EmptyVectorStoreException(f"FAISS 인덱스 파일을 찾을 수 없습니다: {index_file}")
        
        # 메타데이터 로드
        if os.path.exists(metadata_file):
            with open(metadata_file, "rb") as f:
                self.metadata = pickle.load(f)
            print(f"메타데이터 로드 완료. 메타데이터 개수: {len(self.metadata)}")  # 메타데이터 로드 확인
        else:
            raise EmptyVectorStoreException(f"메타데이터 파일을 찾을 수 없습니다: {metadata_file}")
        
        if not self.metadata or not isinstance(self.metadata, list):
            raise EmptyVectorStoreException("메타데이터가 올바르지 않거나 비어 있습니다.")

    def search(self, embedding: np.ndarray, k: int = 5):
        # FAISS 인덱스에서 검색 수행
        D, I = self.index.search(embedding, k)
        print(f"FAISS 검색 완료. 상위 {k}개의 유사도: {D}")  # 검색 결과 확인
        return D, I

# FAISS 인덱스와 메타데이터 파일 경로 설정
index_file_path = "C:\\Users\\201-18\\Documents\\GitHub\\deeplearning\\SPOT\\spot_index.bin"
metadata_file_path = "C:\\Users\\201-18\\Documents\\GitHub\\deeplearning\\SPOT\\spot_metadata.pkl"

# 벡터 저장소 인스턴스 생성
vector_store = FaissVectorStore(index_file=index_file_path, metadata_file=metadata_file_path)

# 텍스트 임베딩 함수 (OpenAI 사용)
def get_openai_embedding(text: str):
    """
    OpenAI를 통해 자연어 임베딩을 생성하는 함수
    :param text: 임베딩 할 텍스트
    :return: 임베딩 벡터
    """
    try:
        embedding = embeddings.embed_query(text)
        print(f"생성된 임베딩 크기: {len(embedding)}")  # 임베딩 크기 확인
        return np.array(embedding, dtype=np.float32)
    except Exception as e:
        raise ValueError(f"임베딩 생성 중 오류 발생: {e}")

# 검색 함수
def search(search_input: str, k: int = 5):
    """
    주어진 검색어에 대해 유사한 항목을 검색하는 함수 (FAISS 중심)
    :param search_input: 검색어
    :param k: 반환할 결과의 수
    :return: 검색 결과 리스트
    """
    if not search_input:
        raise EmptySearchQueryException("검색어를 입력해주세요.")

    # 검색어에 대한 임베딩 생성
    embedding = get_openai_embedding(search_input)

    # 벡터 저장소 차원 확인
    if vector_store.dim is None:
        raise EmptyVectorStoreException("벡터 저장소가 비어 있습니다.")
    print(f"임베딩 차원: {embedding.shape}, FAISS 인덱스 차원: {vector_store.dim}")  # 임베딩과 인덱스 차원 확인

    # 임베딩 차원 조정 (벡터 차원이 맞지 않으면 패딩을 추가)
    if embedding.ndim == 1:
        if len(embedding) < vector_store.dim:
            padding = np.zeros(vector_store.dim - len(embedding), dtype=np.float32)
            embedding = np.concatenate([embedding, padding])
            print(f"임베딩에 패딩 추가. 패딩 후 차원: {embedding.shape}")  # 패딩 후 차원 확인
        elif len(embedding) > vector_store.dim:
            raise ValueError(f"임베딩의 차원이 FAISS 인덱스와 일치하지 않습니다. 예상: {vector_store.dim}, 실제: {len(embedding)}")
    else:
        raise ValueError("임베딩 차원이 올바르지 않습니다.")

    # FAISS 벡터 검색 수행
    embedding = embedding.reshape(1, -1)  # 2차원으로 변환
    try:
        D, I = vector_store.search(embedding, k=k)
    except Exception as e:
        raise ValueError(f"FAISS 검색 중 오류 발생: {e}")

    # 검색 결과 정리 및 반환
    results = []
    for idx in range(len(I[0])):
        i = I[0][idx]
        if i < len(vector_store.metadata):
            meta = vector_store.metadata[i]
            summary = summarize_desc(meta.get("title", "Unknown"), meta.get("summary", ""))
            print(f"결과 {idx+1}: 제목: {meta.get('title', 'Unknown')}, 유사도: {float(D[0][idx])}")  # 검색 결과 확인
            results.append({
                "title": meta.get("title", "Unknown"),
                "similarity": float(D[0][idx]),
                "summary": summary,
                "link": meta.get("link", "https://none")
            })

    if not results:
        raise NoSearchResultsException("검색 결과가 없습니다.")
    
    return results
