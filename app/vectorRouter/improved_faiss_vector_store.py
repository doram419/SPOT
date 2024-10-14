import os
import pickle
import numpy as np
import faiss
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ImprovedFaissVectorStore:
    def __init__(self, index_dir="app/vdb", shard_size=1000000, num_shards=10):
        """
        개선된 Faiss 벡터 저장소 초기화
        :param index_dir: 인덱스 파일을 저장할 디렉토리
        :param shard_size: 각 샤드의 최대 크기
        :param num_shards: 최대 샤드 수
        """
        self.index_dir = index_dir
        self.shard_size = shard_size
        self.num_shards = num_shards
        self.shards = []
        self.metadata = []
        self.dim = None
        self.executor = ThreadPoolExecutor(max_workers=4)  # 비동기 작업을 위한 스레드 풀

        os.makedirs(self.index_dir, exist_ok=True)
        self.load_shards()
        print(f"벡터 저장소 초기화 완료. 상태: {self.get_status()}")

    def load_shards(self):
        """기존 샤드 로드 또는 새 샤드 생성"""
        main_index_file = os.path.join(self.index_dir, "spot_index.bin")
        main_metadata_file = os.path.join(self.index_dir, "spot_metadata.pkl")
        
        if os.path.exists(main_index_file) and os.path.exists(main_metadata_file):
            print(f"메인 인덱스 파일 찾음: {main_index_file}")
            print(f"메인 메타데이터 파일 찾음: {main_metadata_file}")
            # 메인 인덱스와 메타데이터 로드
            self.shards.append(faiss.read_index(main_index_file))
            with open(main_metadata_file, 'rb') as f:
                self.metadata.append(pickle.load(f))
            self.dim = self.shards[0].d
            print(f"메인 인덱스 로드 완료. 차원: {self.dim}, 벡터 수: {self.shards[0].ntotal}")
        else:
            print(f"메인 인덱스 파일 없음: {main_index_file}")
            print(f"메인 메타데이터 파일 없음: {main_metadata_file}")
            print("메인 인덱스 파일이 없습니다. 새 인덱스를 생성합니다.")

        # 추가 샤드 로드
        for i in range(1, self.num_shards):
            shard_file = os.path.join(self.index_dir, f"spot_index_shard_{i}.bin")
            metadata_file = os.path.join(self.index_dir, f"spot_metadata_shard_{i}.pkl")
            
            if os.path.exists(shard_file) and os.path.exists(metadata_file):
                print(f"추가 샤드 파일 찾음: {shard_file}")
                print(f"추가 메타데이터 파일 찾음: {metadata_file}")
                self.shards.append(faiss.read_index(shard_file))
                with open(metadata_file, 'rb') as f:
                    self.metadata.append(pickle.load(f))
                print(f"추가 샤드 {i} 로드 완료. 벡터 수: {self.shards[-1].ntotal}")
            else:
                print(f"추가 샤드 파일 없음: {shard_file}")
                print(f"추가 메타데이터 파일 없음: {metadata_file}")
                break  # 연속된 샤드가 없으면 중단

        if not self.shards:
            print("로드된 샤드가 없습니다. 첫 번째 샤드를 초기화합니다.")
            self.shards.append(None)
            self.metadata.append([])

    def get_status(self):
        """벡터 저장소의 현재 상태를 반환"""
        total_vectors = sum(shard.ntotal for shard in self.shards if shard is not None)
        return {
            "샤드 수": len(self.shards),
            "총 벡터 수": total_vectors,
            "차원": self.dim,
            "메타데이터 항목 수": sum(len(meta) for meta in self.metadata)
        }

    async def search(self, query_vector, k=5):    
        if self.dim is None:
            raise ValueError("인덱스가 비어 있습니다")

        if query_vector.shape[1] != self.dim:
            raise ValueError(f"쿼리 벡터의 차원({query_vector.shape[1]})이 "
                             f"인덱스의 차원({self.dim})과 일치하지 않습니다")
        
        # 모든 샤드에서 검색 수행
        results = await asyncio.gather(*[
            self.search_shard(shard, query_vector, k)
            for shard in self.shards if shard is not None
        ])
        
        print(f"검색이 완료 되었습니다. 결과 수 : {len(results)}")

        if not results:
            print("어떤 샤드에서도 결과를 찾지 못했습니다.")
            return np.array([]), np.array([])

        # 결과 병합 및 정렬
        all_distances = np.concatenate([r[0] for r in results], axis=1)
        all_indices = np.concatenate([r[1] for r in results], axis=1)
        

        if all_distances.size == 0:
            print("No valid distances found")
            return np.array([]), np.array([])

        # 2D 배열을 1D로 변환
        all_distances = all_distances.flatten()
        all_indices = all_indices.flatten()

        # 정렬하여 상위 k개 결과 선택
        sorted_indices = np.argsort(all_distances)[:k]
        top_distances = all_distances[sorted_indices]
        top_indices = all_indices[sorted_indices]

        print(f"최종 결과 - 거리 차원: {top_distances.shape}, 인덱스 차원: {top_indices.shape}")

        return top_distances, top_indices
    
    async def search_shard(self, shard, query_vector, k):
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: shard.search(query_vector, k)
            )
            return result
        except Exception as e:
            print(f"Error in search_shard: {str(e)}")
            return np.array([]), np.array([])  # 빈 결과 반환
    
    def get_metadata(self, indices):
        """
        주어진 인덱스에 해당하는 메타데이터 반환
        """
        metadata = []
        for idx in indices:
            shard_idx = idx // self.shard_size
            local_idx = idx % self.shard_size
            if shard_idx < len(self.metadata) and local_idx < len(self.metadata[shard_idx]):
                metadata.append(self.metadata[shard_idx][local_idx])
        return metadata