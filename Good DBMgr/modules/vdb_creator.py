import tkinter as tk
from tkinter import ttk
from modules.crawling import CrawlingModule

class VdbCreatorModule:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("VDB Creator")
        self.window.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.label = ttk.Label(self.main_frame, text="VDB Creator")
        self.label.pack(pady=10)

        self.crawling_button = ttk.Button(self.main_frame, text="크롤링", command=self.open_crawling)
        self.crawling_button.pack(pady=10)

        # 여기에 새로운 모듈을 위한 버튼을 추가할 수 있습니다.
        self.new_module_button = ttk.Button(self.main_frame, text="새 모듈", command=self.open_new_module)
        self.new_module_button.pack(pady=10)

    def open_crawling(self):
        CrawlingModule(self.parent)

    def open_new_module(self):
        # 새로운 모듈을 여는 함수입니다. 아직 구현되지 않았습니다.
        print("새 모듈 열기 (아직 구현되지 않음)")