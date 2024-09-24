import pickle
import numpy as np
import faiss
import os

class FaissVectorStore:
    def __init__(self, index_file="spot_index.bin", metadata_file="spot_metadata.pkl"):
        self.index_file = index_file
        self.metadata_file = metadata_file
        self.index = None
        self.metadata = list()
        self.load_index()

    def load_index(self):
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.metadata_file, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(1536)  # OpenAI의 text-embedding-3-small 모델은 1536 차원 벡터를 생성합니다.

    def save_index(self):
        faiss.write_index(self.index, self.index_file)
        with open(self.metadata_file, 'wb') as f:
            pickle.dump(self.metadata, f)

    def add_to_index(self, vector_dict, metadata):
        if self.index is None:
            # 첫 번째 벡터의 총 차원 수를 계산합니다
            total_dim = sum(len(v) for v in vector_dict.values() if isinstance(v, (list, np.ndarray)))
            self.index = faiss.IndexFlatL2(total_dim)

        # 딕셔너리의 값들을 하나의 벡터로 연결합니다
        combined_vector = []
        for value in vector_dict.values():
            if isinstance(value, (list, np.ndarray)):
                combined_vector.extend(value)
            elif isinstance(value, (int, float)):
                combined_vector.append(value)

        # numpy 배열로 변환하고 float32 타입으로 지정합니다
        combined_vector = np.array(combined_vector, dtype=np.float32).reshape(1, -1)

        self.index.add(combined_vector)
        self.metadata.append(metadata)
        self.save_index()