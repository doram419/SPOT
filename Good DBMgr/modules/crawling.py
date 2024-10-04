from datetime import datetime
import tkinter as tk
from tkinter import ttk
from .window_utils import position_window

class CrawlingModule:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("크롤링 모듈")
        self.window.geometry("600x400")
        self.crawling_mode = tk.StringVar(value="테스트 모드")  # 기본값을 "test"로 설정
        self.create_widgets()
        
        # 창 크기를 위젯에 맞게 조절
        self.window.update()
        self.window.geometry('')

        position_window(self.parent, self.window)

        # 엔터 키 이벤트 바인딩 추가
        self.window.bind('<Return>', self.on_enter)

    def on_crawl(self):
        keyword = self.keyword_entry.get()
        region = self.region_entry.get()
        mode = self.crawling_mode.get()

        if len(keyword) > 1 and len(region) > 1:
            self.progress_bar['value'] = 0
            self.crawl_button['state'] = 'disabled'
            self.window.after(100, lambda: self.start_crawling(keyword, region, mode))
        else:
            message = "검색어 또는 지역이 누락되었습니다"
            self.update_status(message)
            
    def on_enter(self, event):
        """엔터 키를 눌렀을 때 크롤링 시작"""
        self.on_crawl()

    def start_crawling(self, keyword: str, region: str, mode: str):
        """
        크롤링을 해서 돌려주는 함수
        """
        message = f"키워드: {keyword}, 지역: {region}, 모드: {mode}(으)로 크롤링을 시작합니다"
        self.update_status(message)

        # 크롤링 과정을 시뮬레이션합니다
        for i in range(10):
            # 실제 크롤링 작업을 여기에 구현하세요
            self.window.after(500, lambda p=i: self.update_progress(p * 10))

        self.window.after(5500, self.finish_crawling)

    def update_progress(self, value):
        self.progress_bar['value'] = value
        self.window.update_idletasks()

    def finish_crawling(self):
        self.progress_bar['value'] = 100
        self.update_status("크롤링이 완료되었습니다.")
        self.crawl_button['state'] = 'normal'

    def update_status(self, message: str):
        """
        상태 텍스트 필드를 업데이트 하는 함수
        """
        start_time = datetime.now()
        formatted_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        message = formatted_time + " | " + message
        message = message + "\n"

        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, message)
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')

    def create_widgets(self):
        """
        내부 항목을 추가하는 항목
        """
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 지역 라벨과 입력 필드
        ttk.Label(self.main_frame, text="지역:").grid(row=0, column=0, padx=(0,5), pady=5, sticky='e')
        self.region_entry = ttk.Entry(self.main_frame, width=15)
        self.region_entry.grid(row=0, column=1, padx=(0,15), pady=5, sticky='w')

        # 키워드 라벨과 입력 필드
        ttk.Label(self.main_frame, text="키워드:").grid(row=0, column=2, padx=(0,5), pady=5, sticky='e')
        self.keyword_entry = ttk.Entry(self.main_frame, width=15)
        self.keyword_entry.grid(row=0, column=3, padx=(0,5), pady=5, sticky='w')

        # 크롤링 시작 버튼
        self.crawl_button = ttk.Button(self.main_frame, text="크롤링 시작", command=self.on_crawl)
        self.crawl_button.grid(row=1, column=0, pady=10, sticky='w')

        # 크롤링 시작 버튼에 커맨드 연결
        self.crawl_button = ttk.Button(self.main_frame, text="크롤링 시작", command=self.on_crawl)
        self.crawl_button.grid(row=1, column=0, pady=10, sticky='w')

        # 프로그레스 바 추가
        self.progress_bar = ttk.Progressbar(self.main_frame, orient='horizontal', length=200, mode='determinate')
        self.progress_bar.grid(row=1, column=1, columnspan=3, pady=10, padx=(10, 0), sticky='we')

        # 크롤링 모드 라벨
        ttk.Label(self.main_frame, text="크롤링 모드:").grid(row=2, column=0, padx=(0,5), pady=5, sticky='w')

        # 테스트 모드 라디오 버튼
        ttk.Radiobutton(self.main_frame, text="테스트 모드", 
                        variable=self.crawling_mode, value="테스트 모드").grid(row=2, column=1, padx=(0,5), pady=5, sticky='w')

        # 데이터 수집 모드 라디오 버튼
        ttk.Radiobutton(self.main_frame, text="데이터 수집 모드", 
                        variable=self.crawling_mode, value="데이터 수집 모드").grid(row=2, column=2, padx=(0,5), pady=5, sticky='w')

        # 현재 상태 라벨
        ttk.Label(self.main_frame, text="현재 상태:").grid(row=3, column=0, padx=(0,5), pady=5, sticky='nw')

        # 상태를 표시할 읽기 전용 텍스트 필드
        self.status_text = tk.Text(self.main_frame, height=5, width=50, state='disabled')
        self.status_text.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky='nsew')

        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(self.main_frame, orient='vertical', command=self.status_text.yview)
        scrollbar.grid(row=4, column=4, sticky='ns')
        self.status_text['yscrollcommand'] = scrollbar.set

        # 그리드 설정을 조정하여 텍스트 필드가 창 크기에 맞춰 확장되도록 함
        self.main_frame.columnconfigure(3, weight=1)
        self.main_frame.rowconfigure(4, weight=1)