from tkinter import ttk, Menu
from modules.settings import SettingsWindow
from modules.vdb_creator import VdbCreatorModule
from modules.api_key import ApiKey
from configuration import load_config, save_config

class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Good DB Mgr (proto ver0.7)")

        self.config = load_config()
        self.apply_settings(self.config)
        self.create_widgets()

    def open_settings(self):
        """
        application의 설정창을 여는 항목
        """
        SettingsWindow(self.root, self.config, self.apply_settings) 

    def open_vdb_creator(self):
        VdbCreatorModule(self.root)

    def open_api_status(self):
        """
        api 상태 관리창을 여는 항목
        """
        ApiKey(self.root) 

    def apply_settings(self, new_settings):
        self.config.update(new_settings)
        self.root.option_add("*Font", f"{self.config['font_family']} {self.config['font_size']}")
        
        style = ttk.Style()
        if self.config['theme'] == 'dark':
            style.theme_use('clam')
            style.configure(".", background="gray20", foreground="white")
            style.configure("TSeparator", background="white")
        else:
            style.theme_use('default')
            style.configure("TSeparator", background="gray")
        
        if self.config['button_style'] == 'rounded':
            style.configure('TButton', relief='rounded', padding=6)
        elif self.config['button_style'] == 'flat':
            style.configure('TButton', relief='flat', padding=6)
        
        self.root.update()    

    def create_widgets(self):
        # 메뉴바 생성
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # 설정 메뉴 추가
        settings_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="설정", menu=settings_menu)
        settings_menu.add_command(label="설정 열기", command=self.open_settings)

        # 상태 메뉴 추가
        status_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="상태", menu=status_menu)
        status_menu.add_command(label="api key 관리", command=self.open_api_status)

        # 구분선 추가
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x')

        self.frame = ttk.Frame(self.root)
        self.frame.pack(expand=True, fill='both')

        self.label_frame = ttk.Frame(self.frame, padding="5")
        self.label_frame.pack(pady=10)
        
        self.label = ttk.Label(self.label_frame, text="SPOT DB Mgr")
        self.label.pack()
        self.label = ttk.Label(self.label_frame, text="for Team Spotlight")
        self.label.pack()

        self.button = ttk.Button(self.frame, text="벡터DB 생성하기", command=self.open_vdb_creator)
        self.button.pack(expand=True)

        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(pady=10)

        self.exit_button = ttk.Button(self.button_frame, text="종료", command=self.exit_application)
        self.exit_button.pack(side='left', padx=5)

    def exit_application(self):
        save_config(self.root, self.config)
        self.root.destroy()

    def run(self):
        self.root.geometry(f"{self.config['width']}x{self.config['height']}+{self.config['x']}+{self.config['y']}")
        self.root.protocol("WM_DELETE_WINDOW", lambda: (save_config(self.root, self.config), self.root.destroy()))
        self.root.mainloop()