import pickle
import numpy as np
import faiss
import os

class FaissVectorStore:
    """
    벡터DB 클라이언트 객체
    """
    def __init__(self, index_file="spot_index.bin", 
                 metadata_file="spot_metadata.pkl"):
        """
        클래스를 초기화 하는 함수
        """
        self.index_file = index_file
        self.metadata_file = metadata_file
        self.index = None
        self.metadata = list()

        # 이미 존재하는 인덱스와 메타데이터 로드
        self.load_index()

    def load_index(self):
        """
        내부에 파일이 있으면 그 파일을 읽어들이는 함수
        """
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.metadata_file, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            # 새 인덱스 생성
            self.index = faiss.IndexFlatL2(1536)  # OpenAI의 text-embedding-3-small 모델은 1536 차원 벡터를 생성합니다.

    def save_index(self):
        faiss.write_index(self.index, self.index_file)
        with open(self.metadata_file, 'wb') as f:
            pickle.dump(self.metadata, f)

    def add_to_index(self, vector, metadata):
        if self.index is None:
            self.index = faiss.IndexFlatL2(len(vector))
        self.index.add(np.array([vector], dtype=np.float32))
        self.metadata.append(metadata)
        self.save_index()