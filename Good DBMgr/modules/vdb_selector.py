import tkinter as tk
from tkinter import ttk

class VdbSelectorModule:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("VDB 조회")
        self.window.geometry("400x300")
        self.create_widgets()
        
        self.window.update()
        self.window.geometry('')

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.label = ttk.Label(self.main_frame, text="VDB 조회 모듈")
        self.label.pack(pady=10)

        self.close_button = ttk.Button(self.main_frame, text="종료", command=self.close_window)
        self.close_button.pack(pady=10)

    def close_window(self):
        # 여기에 내부 자원을 정리하는 코드를 추가할 수 있습니다.
        self.window.destroy()
