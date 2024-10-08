import tkinter as tk
from tkinter import ttk
from configuration import update_module_config

class VdbSelectorModule:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.window = tk.Toplevel(parent)
        self.window.title("VDB Selector")
        
        # 저장된 설정 적용
        window_config = config.get('vdb_selector', {})
        self.window.geometry(f"{window_config.get('width', 600)}x{window_config.get('height', 500)}" \
                     f"+{window_config.get('x', 150)}+{window_config.get('y', 150)}")

        
        self.create_widgets()
        
        # 창 닫힐 때 설정 저장
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.label = ttk.Label(self.main_frame, text="VDB Selector Module")
        self.label.pack(pady=10)

        self.close_button = ttk.Button(self.main_frame, text="Close", command=self.on_closing)
        self.close_button.pack(pady=10)

    def on_closing(self):
        update_module_config(self.config, 'vdb_selector', self.window)
        self.window.destroy()