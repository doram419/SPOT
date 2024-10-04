from tkinter import ttk
from settings import SettingsWindow
from modules.crawling import CrawlingModule
from configuration import load_config, save_config

class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Good DB Mgr (ver p0.2)")

        self.config = load_config()
        self.apply_settings(self.config)

        self.create_widgets()

    def open_settings(self):
        """
        application의 설정창을 여는 항목
        """
        SettingsWindow(self.root, self.config, self.apply_settings) 

    def open_crawling(self):
        """
        크롤링 창을 여는 항목
        """
        CrawlingModule(self.root) 

    def apply_settings(self, new_settings):
        self.config.update(new_settings)
        self.root.option_add("*Font", f"{self.config['font_family']} {self.config['font_size']}")
        
        style = ttk.Style()
        if self.config['theme'] == 'dark':
            style.theme_use('clam')
            style.configure(".", background="gray20", foreground="white")
        else:
            style.theme_use('default')
        
        if self.config['button_style'] == 'rounded':
            style.configure('TButton', relief='rounded', padding=6)
        elif self.config['button_style'] == 'flat':
            style.configure('TButton', relief='flat', padding=6)
        
        self.root.update()    

    def create_widgets(self):
        self.frame = ttk.Frame(self.root)
        self.frame.pack(expand=True, fill='both')

        self.label_frame = ttk.Frame(self.frame, padding="5")
        self.label_frame.pack(pady=10)
        
        self.label = ttk.Label(self.label_frame, text="SPOT DB Mgr")
        self.label.pack()
        self.label = ttk.Label(self.label_frame, text="for Team Spotlight")
        self.label.pack()

        self.button = ttk.Button(self.frame, text="크롤링", command=self.open_crawling)
        self.button.pack(expand=True)

        self.settings_button = ttk.Button(self.frame, text="설정", command=self.open_settings)
        self.settings_button.pack(pady=10)

    def run(self):
        self.root.geometry(f"{self.config['width']}x{self.config['height']}+{self.config['x']}+{self.config['y']}")
        self.root.protocol("WM_DELETE_WINDOW", lambda: (save_config(self.root, self.config), self.root.destroy()))
        self.root.mainloop()