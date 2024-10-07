import tkinter as tk
from tkinter import ttk
import json
from typing import List
from .datas.data import Data

class VdbSaveModule:
    def __init__(self, parent, status_module):
        self.parent = parent
        self.status_module = status_module
        self.preprocessed_data = None
        self.create_widgets()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.parent, padding="10")
        
        # VDB 타입 선택
        ttk.Label(self.main_frame, text="VDB 타입:").grid(row=0, column=0, padx=(0,5), pady=5, sticky='e')
        self.vdb_type = tk.StringVar(value="Faiss")
        self.vdb_type_dropdown = ttk.Combobox(self.main_frame, textvariable=self.vdb_type, 
                                              values=["Faiss"], state="readonly", width=15)
        self.vdb_type_dropdown.grid(row=0, column=1, padx=(0,5), pady=5, sticky='w')

        # 저장 경로 입력
        ttk.Label(self.main_frame, text="저장 경로:").grid(row=1, column=0, padx=(0,5), pady=5, sticky='e')
        self.save_path = tk.StringVar(value="./vdb_data")
        self.save_path_entry = ttk.Entry(self.main_frame, textvariable=self.save_path, width=30)
        self.save_path_entry.grid(row=1, column=1, columnspan=2, padx=(0,5), pady=5, sticky='w')

        # 저장 버튼
        self.save_button = ttk.Button(self.main_frame, text="VDB 저장", command=self.save_to_vdb)
        self.save_button.grid(row=2, column=1, pady=10)

    def set_preprocessed_data(self, data: List[Data]):
        self.preprocessed_data = data
        self.status_module.update_status("전처리된 데이터 수신 완료")

    def save_to_vdb(self):
        if self.preprocessed_data is None:
            self.status_module.update_status("저장할 데이터가 없습니다.")
            return

        vdb_type = self.vdb_type.get()
        save_path = self.save_path.get()

        self.status_module.update_status(f"{vdb_type} VDB에 데이터 저장 시작...")

        # 여기에 실제 VDB 저장 로직을 구현합니다.
        # 예를 들어, Chroma를 사용한다면:
        if vdb_type == "Chroma":
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
                
                self.status_module.update_status("VDB 저장 완료")
            except Exception as e:
                self.status_module.update_status(f"VDB 저장 중 오류 발생: {str(e)}")
        else:
            self.status_module.update_status(f"{vdb_type} VDB 저장은 아직 구현되지 않았습니다.")

    def get_widget(self):
        return self.main_frame