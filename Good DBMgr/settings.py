import tkinter as tk
from tkinter import ttk

class SettingsWindow:
    def __init__(self, parent, current_settings, apply_settings):
        self.parent = parent
        self.settings = current_settings
        self.apply_settings = apply_settings

        self.window = tk.Toplevel(parent)
        self.window.title("설정")
        self.window.geometry("300x250")

        self.create_widgets()

    def create_widgets(self):
        # 폰트 설정
        ttk.Label(self.window, text="폰트:").grid(row=0, column=0, padx=5, pady=5)
        self.font_combo = ttk.Combobox(self.window, values=["Arial", "Helvetica", "Times New Roman"])
        self.font_combo.set(self.settings["font_family"])
        self.font_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.window, text="폰트 크기:").grid(row=1, column=0, padx=5, pady=5)
        self.font_size = tk.Spinbox(self.window, from_=8, to=20, width=5)
        self.font_size.delete(0, "end")
        self.font_size.insert(0, self.settings["font_size"])
        self.font_size.grid(row=1, column=1, padx=5, pady=5)

        # 테마 설정
        ttk.Label(self.window, text="테마:").grid(row=2, column=0, padx=5, pady=5)
        self.theme_combo = ttk.Combobox(self.window, values=["light", "dark"])
        self.theme_combo.set(self.settings["theme"])
        self.theme_combo.grid(row=2, column=1, padx=5, pady=5)

        # 버튼 스타일 설정
        ttk.Label(self.window, text="버튼 스타일:").grid(row=3, column=0, padx=5, pady=5)
        self.button_style_combo = ttk.Combobox(self.window, values=["default", "rounded", "flat"])
        self.button_style_combo.set(self.settings["button_style"])
        self.button_style_combo.grid(row=3, column=1, padx=5, pady=5)

        # 적용 버튼
        ttk.Button(self.window, text="적용", command=self.apply).grid(row=4, column=0, columnspan=2, pady=20)

    def apply(self):
        new_settings = {
            "font_family": self.font_combo.get(),
            "font_size": int(self.font_size.get()),
            "theme": self.theme_combo.get(),
            "button_style": self.button_style_combo.get()
        }
        self.apply_settings(new_settings)
        self.window.destroy()
