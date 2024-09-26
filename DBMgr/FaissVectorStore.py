import pickle
import numpy as np
import faiss
import os

class FaissVectorStore:
    def __init__(self, index_file="spot_index.bin", metadata_file="spot_metadata.pkl"):
        """
        FaissVectorStore 클래스를 초기화합니다.
        :param index_file: Faiss 인덱스를 저장할 파일 이름
        :param metadata_file: 메타데이터를 저장할 파일 이름
        """
        self.index_file = index_file
        self.metadata_file = metadata_file
        self.index = None
        self.metadata = list()
        self.dim = None  
        self.load_index()

    def load_index(self):
        """
        저장된 인덱스와 메타데이터를 로드합니다. 파일이 없으면 새 인덱스를 생성합니다.
        """
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            self.index = faiss.read_index(self.index_file)
            self.dim = self.index.d
            with open(self.metadata_file, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            self.index = None
            self.dim = None
            # self.index = faiss.IndexFlatL2(1536)  # OpenAI의 text-embedding-3-small 모델은 1536 차원 벡터를 생성합니다.

    def save_index(self):
        """
        현재 인덱스와 메타데이터를 파일에 저장합니다.
        """
        if self.index is not None:
            faiss.write_index(self.index, self.index_file)
        with open(self.metadata_file, 'wb') as f:
            pickle.dump(self.metadata, f)

    def add_to_index(self, vector_dict, metadata):
        """
        벡터 딕셔너리와 메타데이터를 인덱스에 추가합니다.
        :param vector_dict: 추가할 벡터 데이터가 포함된 딕셔너리
        :param metadata: 벡터와 연관된 메타데이터
        """

        # 딕셔너리의 값들을 하나의 리스트로 연결합니다
        combined_vector = np.concatenate([v.flatten() for v in vector_dict.values()])

        if self.index is None:
            self.dim = combined_vector.shape[0]
            self.index = faiss.IndexFlatL2(self.dim)

        combined_vector = combined_vector.reshape(1, -1)
        self.index.add(combined_vector)
        self.metadata.append(metadata)
        self.save_index()

    def search(self, query_vector, k=5):
            """
            주어진 쿼리 벡터와 가장 유사한 k개의 벡터를 검색합니다.
            :param query_vector: 검색할 쿼리 벡터
            :param k: 반환할 결과의 개수
            :return: 거리와 인덱스의 튜플
            """
            if self.index is None:
                raise ValueError("인덱스가 초기화되지 않았습니다.")
        
            query_vector = query_vector.reshape(1, -1)
            if query_vector.shape[1] != self.dim:
                raise ValueError(f"쿼리 벡터의 차원({query_vector.shape[1]})이 인덱스의 차원({self.dim})과 일치하지 않습니다.")
            
            return self.index.search(query_vector, k)