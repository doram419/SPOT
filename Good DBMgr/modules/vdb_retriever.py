import tkinter as tk
from tkinter import ttk
from configuration import update_module_config

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

        self.create_widgets()
        
        # 창 닫힐 때 설정 저장
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 쿼리 입력 섹션
        query_frame = ttk.Frame(self.main_frame)
        query_frame.pack(fill=tk.X, pady=(0, 10))

        self.query_label = ttk.Label(query_frame, text="쿼리:")
        self.query_label.pack(side=tk.LEFT, padx=(0, 5))

        self.query_entry = ttk.Entry(query_frame)
        self.query_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.search_button = ttk.Button(query_frame, text="검색", command=self.search)
        self.search_button.pack(side=tk.LEFT, padx=(5, 0))

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

        self.close_button = ttk.Button(self.main_frame, text="Close", command=self.on_closing)
        self.close_button.pack(pady=(10, 0))

    def search(self):
        # 여기에 검색 로직을 구현합니다
        query = self.query_entry.get()
        
        # 임시 결과 (실제 검색 결과로 대체해야 함)
        result = f"Query: {query}\n\nSearch results will be displayed here."
        
        # 결과 텍스트 위젯 업데이트
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)
        self.result_text.config(state="disabled")

    def on_closing(self):
        update_module_config(self.config, 'vdb_retriever', self.window)
        self.window.destroy()