import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import pickle
import json
import csv

class VdbSelectorModule:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.window = tk.Toplevel(parent)
        self.window.title("VDB 출력하기")
        
        # 저장된 설정 적용
        window_config = config.get('vdb_selector', {})
        self.window.geometry(f"{window_config.get('width', 600)}x{window_config.get('height', 400)}" \
                     f"+{window_config.get('x', 150)}+{window_config.get('y', 150)}")
        
        # 기본 경로 설정
        self.default_path = './vdb_data'
        self.ensure_default_path()
        
        # 메타데이터 파일 이름 설정
        self.meta_name = 'spot_metadata'
        self.meta_file_name = os.path.join(self.default_path, f'{self.meta_name}.pkl')

        self.create_widgets()

    def ensure_default_path(self):
        if not os.path.exists(self.default_path):
            os.makedirs(self.default_path)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # "출력하기" 라벨
        self.title_label = ttk.Label(self.main_frame, text="출력하기", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # 경로 입력
        self.path_frame = ttk.Frame(self.main_frame)
        self.path_frame.pack(fill=tk.X, pady=5)
        self.path_label = ttk.Label(self.path_frame, text="경로:")
        self.path_label.pack(side=tk.LEFT, padx=(0, 5))
        self.path_entry = ttk.Entry(self.path_frame)
        self.path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.path_entry.insert(0, self.default_path)
        self.browse_button = ttk.Button(self.path_frame, text="Browse", command=self.browse_path)
        self.browse_button.pack(side=tk.LEFT, padx=(5, 0))

        # 파일 형식 선택
        self.format_frame = ttk.Frame(self.main_frame)
        self.format_frame.pack(fill=tk.X, pady=5)
        self.format_label = ttk.Label(self.format_frame, text="형식:")
        self.format_label.pack(side=tk.LEFT, padx=(0, 5))
        self.format_combobox = ttk.Combobox(self.format_frame, values=["CSV", "JSON", "TXT"])
        self.format_combobox.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.format_combobox.set("CSV")  # 기본값 설정

        # 출력 버튼
        self.output_button = ttk.Button(self.main_frame, text="출력", command=self.output)
        self.output_button.pack(pady=10)

    def browse_path(self):
        path = filedialog.askdirectory(initialdir=self.default_path)
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def output(self):
        path = self.path_entry.get()
        format = self.format_combobox.get()
        self.print_meta(path, format)

    def print_meta(self, path, format):
        """메타 데이터를 지정된 형식으로 출력하는 함수"""
        try:
            with open(self.meta_file_name, 'rb') as f:
                data = pickle.load(f)
            
            file_name = f'pkl_output.{format.lower()}'
            full_path = os.path.join(path, file_name)
            
            if format == 'CSV':
                with open(full_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for i, d in enumerate(data):
                        writer.writerow([i, d])
            elif format == 'JSON':
                with open(full_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format == 'TXT':
                with open(full_path, 'w', encoding='utf-8') as f:
                    for i, d in enumerate(data):
                        word = f"{i} : {d}\n"
                        f.write(word)
                print(f"메타데이터를 {full_path}로 저장했습니다")
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            messagebox.showinfo("성공", f"메타데이터를 {full_path}로 저장했습니다")
        except Exception as e:
            messagebox.showerror("오류", f"메타데이터 출력 중 오류 발생: {str(e)}")

    def on_closing(self):
        self.window.destroy()