import tkinter as tk
from tkinter import ttk
from modules.crawling import CrawlingModule
from configuration import update_module_config

class VdbCreatorModule:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.window = tk.Toplevel(parent)
        self.window.title("VDB Creator")
        
        # 저장된 설정 적용
        window_config = config.get('vdb_creator', {})
        self.window.geometry(f"{window_config.get('width', 600)}x{window_config.get('height', 500)}" \
                     f"+{window_config.get('x', 150)}+{window_config.get('y', 150)}")

        
        self.create_widgets()
        
        # 창 닫힐 때 설정 저장
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.label = ttk.Label(self.main_frame, text="VDB Creator")
        self.label.pack(pady=10)

        # 탭 컨트롤 생성
        self.tab_control = ttk.Notebook(self.main_frame)
        
        # 크롤링 탭
        crawling_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(crawling_tab, text='크롤링')
        
        # CrawlingModule의 위젯 추가
        crawling_module = CrawlingModule(crawling_tab)
        crawling_widget = crawling_module.get_widget()
        crawling_widget.pack(fill=tk.BOTH, expand=True)

        # 데이터 처리 탭 (새로운 모듈)
        data_processing_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(data_processing_tab, text='데이터 처리')
        
        # 데이터 처리 탭의 내용 (임시)
        ttk.Label(data_processing_tab, text="데이터 처리 모듈이 여기에 구현될 예정입니다.").pack(pady=20)
        ttk.Button(data_processing_tab, text="데이터 처리 시작", command=self.start_data_processing).pack(pady=10)

        # 벡터 생성 탭 (새로운 모듈)
        vector_creation_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(vector_creation_tab, text='벡터 생성')
        
        # 벡터 생성 탭의 내용 (임시)
        ttk.Label(vector_creation_tab, text="벡터 생성 모듈이 여기에 구현될 예정입니다.").pack(pady=20)
        ttk.Button(vector_creation_tab, text="벡터 생성 시작", command=self.start_vector_creation).pack(pady=10)

        self.tab_control.pack(expand=1, fill="both")

    def start_data_processing(self):
        print("데이터 처리 시작 (아직 구현되지 않음)")

    def start_vector_creation(self):
        print("벡터 생성 시작 (아직 구현되지 않음)")
    
    def on_closing(self):
        update_module_config(self.config, 'vdb_creator', self.window)
        self.window.destroy()