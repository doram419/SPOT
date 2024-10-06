from datetime import datetime
import threading
import tkinter as tk
from tkinter import ttk
from .datas.constants import (EMBEDDING_MODEL_TYPES, EMBEDDING_MODEL_VERSIONS,
                              VECTOR_DBS, SUMMARY_MODEL_TYPES, SUMMARY_MODEL_VERSIONS)

class PreprocessingModule:
    def __init__(self, parent, status_module):
        self.parent = parent
        self.status_module = status_module
        self.create_widgets()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.parent, padding="10")
        
        # 임베딩 모델 선택
        ttk.Label(self.main_frame, text="임베딩 모델:").grid(row=0, column=0, padx=(0,5), pady=5, sticky='e')
        self.embedding_model_type = tk.StringVar()
        self.embedding_type_dropdown = ttk.Combobox(self.main_frame, textvariable=self.embedding_model_type, 
                                                    values=EMBEDDING_MODEL_TYPES, state="readonly", width=15)
        self.embedding_type_dropdown.grid(row=0, column=1, padx=(0,5), pady=5, sticky='w')
        self.embedding_type_dropdown.set(EMBEDDING_MODEL_TYPES[0])
        self.embedding_type_dropdown.bind("<<ComboboxSelected>>", self.update_embedding_versions)

        self.embedding_model_version = tk.StringVar()
        self.embedding_version_dropdown = ttk.Combobox(self.main_frame, textvariable=self.embedding_model_version, 
                                                       state="readonly", width=20)
        self.embedding_version_dropdown.grid(row=0, column=2, padx=(0,15), pady=5, sticky='w')
        self.update_embedding_versions()

        # VectorDB 선택
        ttk.Label(self.main_frame, text="Vector DB:").grid(row=1, column=0, padx=(0,5), pady=5, sticky='e')
        self.vector_db = tk.StringVar()
        self.vector_db_dropdown = ttk.Combobox(self.main_frame, textvariable=self.vector_db, 
                                               values=VECTOR_DBS, state="readonly", width=30)
        self.vector_db_dropdown.grid(row=1, column=1, columnspan=2, padx=(0,15), pady=5, sticky='w')
        self.vector_db_dropdown.set(VECTOR_DBS[0])

        # 요약 모델 선택
        ttk.Label(self.main_frame, text="요약 모델:").grid(row=2, column=0, padx=(0,5), pady=5, sticky='e')
        self.summary_model_type = tk.StringVar()
        self.summary_type_dropdown = ttk.Combobox(self.main_frame, textvariable=self.summary_model_type, 
                                                  values=SUMMARY_MODEL_TYPES, state="readonly", width=15)
        self.summary_type_dropdown.grid(row=2, column=1, padx=(0,5), pady=5, sticky='w')
        self.summary_type_dropdown.set(SUMMARY_MODEL_TYPES[0])
        self.summary_type_dropdown.bind("<<ComboboxSelected>>", self.update_summary_versions)

        self.summary_model_version = tk.StringVar()
        self.summary_version_dropdown = ttk.Combobox(self.main_frame, textvariable=self.summary_model_version, 
                                                     state="readonly", width=20)
        self.summary_version_dropdown.grid(row=2, column=2, padx=(0,15), pady=5, sticky='w')
        self.update_summary_versions()

        # 청킹 사이즈 입력
        ttk.Label(self.main_frame, text="청킹 사이즈:").grid(row=3, column=0, padx=(0,5), pady=5, sticky='e')
        self.chunk_size = tk.StringVar(value="200")
        self.chunk_size_entry = ttk.Entry(self.main_frame, textvariable=self.chunk_size, width=10)
        self.chunk_size_entry.grid(row=3, column=1, padx=(0,15), pady=5, sticky='w')

        # 오버랩 입력
        ttk.Label(self.main_frame, text="오버랩:").grid(row=4, column=0, padx=(0,5), pady=5, sticky='e')
        self.overlap = tk.StringVar(value="100")
        self.overlap_entry = ttk.Entry(self.main_frame, textvariable=self.overlap, width=10)
        self.overlap_entry.grid(row=4, column=1, padx=(0,15), pady=5, sticky='w')

        # 전처리 시작 버튼
        self.preprocess_button = ttk.Button(self.main_frame, text="전처리 시작", command=self.start_preprocessing)
        self.preprocess_button.grid(row=5, column=0, columnspan=3, pady=10)

    def update_embedding_versions(self, event=None):
        selected_type = self.embedding_model_type.get()
        versions = EMBEDDING_MODEL_VERSIONS.get(selected_type, [])
        self.embedding_version_dropdown['values'] = versions
        if versions:
            self.embedding_version_dropdown.set(versions[0])
        else:
            self.embedding_version_dropdown.set('')

    def update_summary_versions(self, event=None):
        selected_type = self.summary_model_type.get()
        versions = SUMMARY_MODEL_VERSIONS.get(selected_type, [])
        self.summary_version_dropdown['values'] = versions
        if versions:
            self.summary_version_dropdown.set(versions[0])
        else:
            self.summary_version_dropdown.set('')

    def start_preprocessing(self):
        embedding_type = self.embedding_model_type.get()
        embedding_version = self.embedding_model_version.get()
        vector_db = self.vector_db.get()
        summary_type = self.summary_model_type.get()
        summary_version = self.summary_model_version.get()
        chunk_size = self.chunk_size.get()
        overlap = self.overlap.get()
        
        # 상태 업데이트
        self.status_module.update_status(
            f"\n=====전처리 시작=====\n"
            f"임베딩 모델 - {embedding_type}/{embedding_version}\n"
            f"DB - {vector_db}, 요약 모델 - {summary_type}/{summary_version}\n"
            f"청킹 사이즈 - {chunk_size}, 오버랩 - {overlap}\n"
        )

    def get_widget(self):
        return self.main_frame