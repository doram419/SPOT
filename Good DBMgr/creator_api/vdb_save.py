import tkinter as tk
from tkinter import ttk
import json
import os
from .datas.constants import VECTOR_DBS

class VdbSaveModule:
    def __init__(self, parent, status_module):
        self.parent = parent
        self.status_module = status_module
        self.preprocessed_data = None
        self.create_widgets()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # VDB 타입 선택
        vdb_type_frame = ttk.Frame(self.main_frame)
        vdb_type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(vdb_type_frame, text="VDB 타입:").pack(side=tk.LEFT, padx=(0, 5))
        self.vdb_type = tk.StringVar(value=VECTOR_DBS[0])
        self.vdb_type_dropdown = ttk.Combobox(vdb_type_frame, textvariable=self.vdb_type, 
                                              values=VECTOR_DBS, state="readonly", width=15)
        self.vdb_type_dropdown.pack(side=tk.LEFT)

        # 저장 경로 입력
        save_path_frame = ttk.Frame(self.main_frame)
        save_path_frame.pack(fill=tk.X, pady=5)
        ttk.Label(save_path_frame, text="저장 경로:").pack(side=tk.LEFT, padx=(0, 5))
        self.save_path = tk.StringVar(value="./vdb_data")
        self.save_path_entry = ttk.Entry(save_path_frame, textvariable=self.save_path, width=30)
        self.save_path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

    def set_preprocessed_data(self, data):
        self.preprocessed_data = data
        self.status_module.update_status("전처리된 데이터 수신 완료")

    async def save_to_vdb(self):
        if self.preprocessed_data is None:
            self.status_module.update_status("저장할 데이터가 없습니다.")
            return False

        vdb_type = self.vdb_type.get()
        save_path = self.save_path.get()

        self.status_module.update_status(f"{vdb_type} VDB에 데이터 저장 시작...")

        # 저장 경로가 존재하지 않으면 생성
        os.makedirs(save_path, exist_ok=True)

        if vdb_type == "Chroma":
            success = await self.save_to_chroma(save_path)
        elif vdb_type == "Faiss":
            success = await self.save_to_faiss(save_path)
        else:
            self.status_module.update_status(f"{vdb_type} VDB 저장은 아직 구현되지 않았습니다.")
            return False

        if success:
            self.status_module.update_status(f"{vdb_type} VDB 저장 완료")
        else:
            self.status_module.update_status(f"{vdb_type} VDB 저장 실패")

        return success

    async def save_to_chroma(self, save_path):
        try:
            from chromadb import Client, Settings
            client = Client(Settings(persist_directory=save_path))
            collection = client.create_collection("my_collection")
            
            for data in self.preprocessed_data:
                # Google 데이터 저장
                for chunk in data.google_json:
                    collection.add(
                        embeddings=chunk['content'].tolist(),  # numpy array를 list로 변환
                        documents=json.dumps(chunk['chunk']),
                        metadatas={"source": "google", "name": data.name}
                    )
                
                # Naver 블로그 데이터 저장
                for blog_data in data.blog_datas:
                    for chunk in blog_data.content:
                        collection.add(
                            embeddings=chunk['content'].tolist(),  # numpy array를 list로 변환
                            documents=json.dumps(chunk['chunk']),
                            metadatas={"source": "naver", "name": data.name, "blog_url": blog_data.blog_url}
                        )
            
            return True
        except Exception as e:
            self.status_module.update_status(f"Chroma VDB 저장 중 오류 발생: {str(e)}")
            return False

    async def save_to_faiss(self, save_path):
        try:
            import faiss
            import numpy as np
            
            # Faiss 인덱스 생성
            dimension = len(self.preprocessed_data[0].google_json[0]['content'])  # 첫 번째 임베딩의 차원을 사용
            index = faiss.IndexFlatL2(dimension)
            
            all_embeddings = []
            all_metadata = []
            
            for data in self.preprocessed_data:
                # Google 데이터 처리
                for chunk in data.google_json:
                    all_embeddings.append(chunk['content'])
                    all_metadata.append({
                        "source": "google",
                        "name": data.name,
                        "content": json.dumps(chunk['chunk'])
                    })
                
                # Naver 블로그 데이터 처리
                for blog_data in data.blog_datas:
                    for chunk in blog_data.content:
                        all_embeddings.append(chunk['content'])
                        all_metadata.append({
                            "source": "naver",
                            "name": data.name,
                            "blog_url": blog_data.blog_url,
                            "content": json.dumps(chunk['chunk'])
                        })
            
            # numpy array로 변환하여 Faiss 인덱스에 추가
            embeddings_array = np.array(all_embeddings).astype('float32')
            index.add(embeddings_array)
            
            # 인덱스와 메타데이터 저장
            faiss.write_index(index, os.path.join(save_path, "faiss_index.idx"))
            with open(os.path.join(save_path, "metadata.json"), 'w', encoding='utf-8') as f:
                json.dump(all_metadata, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            self.status_module.update_status(f"Faiss VDB 저장 중 오류 발생: {str(e)}")
            return False

    def get_widget(self):
        return self.main_frame