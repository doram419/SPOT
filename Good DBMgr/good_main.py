
"""
웹 크롤링을 통해서 Faiss DB를 만드는 프로그램
"""
import tkinter as tk
from ttkthemes import ThemedTk
from application import Application

if __name__ == "__main__":
    root = ThemedTk(theme="arc")  # 기본 테마를 'arc'로 설정
    icon = tk.PhotoImage(file="logo.png")
    root.wm_iconphoto(True, icon)   
    app = Application(root)
    app.run()