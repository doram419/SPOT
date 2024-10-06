import tkinter as tk
from tkinter import ttk
from creator_api.crawling import CrawlingModule
from configuration import update_module_config
from .status_module import StatusModule

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

        # grid 설정
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=0)
        self.main_frame.rowconfigure(3, weight=0)

        # 라벨
        self.label = ttk.Label(self.main_frame, text="VDB Creator")
        self.label.grid(row=0, column=0, pady=10, sticky='nw')

        # 탭 컨트롤 생성
        self.tab_control = ttk.Notebook(self.main_frame)
        self.tab_control.grid(row=1, column=0, sticky='nsew')
        
        # 상태 모듈 추가
        status_frame = ttk.Frame(self.main_frame)
        status_frame.grid(row=2, column=0, pady=10, sticky='nsew')
        self.status_module = StatusModule(status_frame)

        # 크롤링 탭
        crawling_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(crawling_tab, text='크롤링')
        
        # CrawlingModule의 위젯 추가 (status_module 전달)
        crawling_module = CrawlingModule(crawling_tab, self.status_module)
        crawling_widget = crawling_module.get_widget()
        crawling_widget.pack(fill=tk.BOTH, expand=True)

        # 데이터 처리 탭 (새로운 모듈)
        data_processing_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(data_processing_tab, text='데이터 전처리')
        
        # 데이터 처리 탭의 내용 (임시)
        ttk.Label(data_processing_tab, text="데이터 처리 모듈이 여기에 구현될 예정입니다.").pack(pady=20)
        ttk.Button(data_processing_tab, text="데이터 처리 시작", command=self.start_data_processing).pack(pady=10)

        # 벡터 생성 탭 (새로운 모듈)
        vector_creation_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(vector_creation_tab, text='벡터 생성')
        
        # 벡터 생성 탭의 내용 (임시)
        ttk.Label(vector_creation_tab, text="벡터 생성 모듈이 여기에 구현될 예정입니다.").pack(pady=20)
        ttk.Button(vector_creation_tab, text="벡터 생성 시작", command=self.start_vector_creation).pack(pady=10)

        # 종료 버튼 추가
        self.close_button = ttk.Button(self.main_frame, text="Close", command=self.on_closing)
        self.close_button.grid(row=3, column=0, pady=10, sticky='se')

    def start_data_processing(self):
        self.status_module.update_status("데이터 처리 시작 (아직 구현되지 않음)")

    def start_vector_creation(self):
        self.status_module.update_status("벡터 생성 시작 (아직 구현되지 않음)")
    
    def on_closing(self):
        update_module_config(self.config, 'vdb_creator', self.window)
        self.window.destroy()