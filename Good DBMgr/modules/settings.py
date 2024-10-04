import tkinter as tk
from tkinter import ttk
from .window_utils import position_window

class SettingsWindow:
    def __init__(self, parent, current_settings, apply_settings):
        self.parent = parent
        self.settings = current_settings
        self.apply_settings = apply_settings

        self.window = tk.Toplevel(parent)
        self.window.title("설정")
        self.window.resizable(False, False)

        self.create_widgets()
        
        # 창 크기를 위젯에 맞게 조절
        self.window.update()
        self.window.geometry('')

        # 부모 창의 오른쪽에 설정 창 배치
        position_window(self.parent, self.window)

    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 폰트 설정
        ttk.Label(main_frame, text="폰트:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.font_combo = ttk.Combobox(main_frame, values=["Arial", "Helvetica", "Verdana", "Tahoma"])
        self.font_combo.set(self.settings["font_family"])
        self.font_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 폰트 크기 설정
        ttk.Label(main_frame, text="폰트 크기:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.font_size = tk.Spinbox(main_frame, from_=8, to=20, width=5)
        self.font_size.delete(0, "end")
        self.font_size.insert(0, self.settings["font_size"])
        self.font_size.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # 테마 설정
        ttk.Label(main_frame, text="테마:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.theme_combo = ttk.Combobox(main_frame, values=["light", "dark"])
        self.theme_combo.set(self.settings["theme"])
        self.theme_combo.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # 버튼 스타일 설정
        ttk.Label(main_frame, text="버튼 스타일:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.button_style_combo = ttk.Combobox(main_frame, values=["default", "rounded", "flat"])
        self.button_style_combo.set(self.settings["button_style"])
        self.button_style_combo.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        # 적용 버튼
        ttk.Button(main_frame, text="적용", command=self.apply).grid(row=4, column=0, columnspan=2, pady=20)

    def apply(self):
        new_settings = {
            "font_family": self.font_combo.get(),
            "font_size": int(self.font_size.get()),
            "theme": self.theme_combo.get(),
            "button_style": self.button_style_combo.get()
        }
        self.apply_settings(new_settings)
        self.window.destroy()