import tkinter as tk
from tkinter import ttk
from configuration import update_module_config
from .faissVectorStore import FaissVectorStore
from .embeddings import EmbeddingModule
from .datas.constants import EMBEDDING_MODEL_TYPES, EMBEDDING_MODEL_VERSIONS
import numpy as np

class VdbRetrieverModule:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.window = tk.Toplevel(parent)
        self.window.title("VDB Retriever")
        
        # 저장된 설정 적용
        window_config = config.get('vdb_retriever', {})
        self.window.geometry(f"{window_config.get('width', 600)}x{window_config.get('height', 500)}" \
                     f"+{window_config.get('x', 150)}+{window_config.get('y', 150)}")
        
        # FaissVectorStore 인스턴스 생성
        self.vector_store = FaissVectorStore() 
        # EmbeddingModule 인스턴스는 나중에 생성 
        self.embedding = None  
        self.create_widgets()
        
        # 창 닫힐 때 설정 저장
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 임베딩 모델 선택
        embedding_frame = ttk.Frame(self.main_frame)
        embedding_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(embedding_frame, text="임베딩 모델:").pack(side=tk.LEFT, padx=(0, 5))
        self.embedding_model_type = tk.StringVar()
        self.embedding_type_dropdown = ttk.Combobox(embedding_frame, textvariable=self.embedding_model_type, 
                                                    values=EMBEDDING_MODEL_TYPES, state="readonly", width=15)
        self.embedding_type_dropdown.pack(side=tk.LEFT, padx=(0, 5))
        self.embedding_type_dropdown.set(EMBEDDING_MODEL_TYPES[0])
        self.embedding_type_dropdown.bind("<<ComboboxSelected>>", self.update_embedding_versions)

        self.embedding_model_version = tk.StringVar()
        self.embedding_version_dropdown = ttk.Combobox(embedding_frame, textvariable=self.embedding_model_version, 
                                                       state="readonly", width=20)
        self.embedding_version_dropdown.pack(side=tk.LEFT, padx=(0, 5))
        self.update_embedding_versions()

        # 쿼리 입력 섹션
        query_frame = ttk.Frame(self.main_frame)
        query_frame.pack(fill=tk.X, pady=(0, 10))

        self.query_label = ttk.Label(query_frame, text="쿼리:")
        self.query_label.pack(side=tk.LEFT, padx=(0, 5))

        self.query_entry = ttk.Entry(query_frame)
        self.query_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.search_button = ttk.Button(query_frame, text="검색", command=self.search)
        self.search_button.pack(side=tk.LEFT, padx=(5, 0))

        # 결과 개수 조절 섹션
        count_frame = ttk.Frame(self.main_frame)
        count_frame.pack(fill=tk.X, pady=(0, 10))

        self.count_label = ttk.Label(count_frame, text="결과 개수:")
        self.count_label.pack(side=tk.LEFT, padx=(0, 5))

        self.count_var = tk.StringVar(value="5")
        self.count_entry = ttk.Entry(count_frame, textvariable=self.count_var, width=5)
        self.count_entry.pack(side=tk.LEFT)

        self.increase_button = ttk.Button(count_frame, text="+", command=self.increase_count, width=2)
        self.increase_button.pack(side=tk.LEFT, padx=(5, 0))

        self.decrease_button = ttk.Button(count_frame, text="-", command=self.decrease_count, width=2)
        self.decrease_button.pack(side=tk.LEFT, padx=(5, 0))

        # 결과 표시 섹션
        result_frame = ttk.Frame(self.main_frame)
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_label = ttk.Label(result_frame, text="결과:")
        self.result_label.pack(anchor=tk.W)

        self.result_text = tk.Text(result_frame, wrap=tk.WORD, state="disabled")
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.configure(yscrollcommand=scrollbar.set)

        # 상태 메시지
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.pack(pady=(10, 0))

        self.close_button = ttk.Button(self.main_frame, text="Close", command=self.on_closing)
        self.close_button.pack(pady=(10, 0))

    def update_embedding_versions(self, event=None):
        selected_type = self.embedding_model_type.get()
        versions = EMBEDDING_MODEL_VERSIONS.get(selected_type, [])
        self.embedding_version_dropdown['values'] = versions
        if versions:
            self.embedding_version_dropdown.set(versions[0])
        else:
            self.embedding_version_dropdown.set('')

    def increase_count(self):
        current = int(self.count_var.get())
        self.count_var.set(str(current + 1))

    def decrease_count(self):
        current = int(self.count_var.get())
        if current > 1:
            self.count_var.set(str(current - 1))

    def search(self):
        query = self.query_entry.get()
        k = int(self.count_var.get())

        embedding_type = self.embedding_model_type.get()
        embedding_version = self.embedding_model_version.get()

        if self.embedding is None or self.embedding.model_name != embedding_type or self.embedding.version != embedding_version:
            self.embedding = EmbeddingModule(model_name=embedding_type, version=embedding_version)

        try:
            query_vector = self.embedding.get_text_embedding(query)
            
            distances, indices = self.vector_store.search(query_vector, k)
            
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0]), 1):
                if idx < len(self.vector_store.metadata):
                    metadata = self.vector_store.metadata[idx]
                    results.append(f"{i}. Distance: {distance:.4f}, Metadata: {metadata}")
                else:
                    break

            if len(results) < k:
                self.status_var.set(f"주의: 요청한 {k}개의 결과 중 {len(results)}개만 찾았습니다.")
            else:
                self.status_var.set("검색 완료")

            # 결과 텍스트 위젯 업데이트
            self.result_text.config(state="normal")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "\n".join(results))
            self.result_text.config(state="disabled")

        except Exception as e:
            self.status_var.set(f"검색 중 오류 발생: {str(e)}")

    def on_closing(self):
        update_module_config(self.config, 'vdb_retriever', self.window)
        self.window.destroy()