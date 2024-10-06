import tkinter as tk
from tkinter import ttk
from modules.crawling import CrawlingModule

class VdbCreatorModule:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("VDB Creator")
        self.window.geometry("600x500")
        self.create_widgets()
        
        self.window.update()
        self.window.geometry('')

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