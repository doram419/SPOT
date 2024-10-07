
"""
웹 크롤링을 통해서 Faiss DB를 만드는 프로그램
"""
import tkinter as tk
from Application import Application

if __name__ == "__main__":
    root = tk.Tk()
    icon = tk.PhotoImage(file="logo.png")
    root.wm_iconphoto(True, icon)
    app = Application(root)
    app.run()