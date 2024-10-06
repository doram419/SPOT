from datetime import datetime
import threading
import tkinter as tk
from tkinter import ttk
from .window_utils import position_window
from .api_key import get_key
from .google_service import GoogleService
from .datas.constants import TEST_MODE, GATHER_MODE

class CrawlingModule:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("크롤링 모듈")
        self.window.geometry("600x400")
        self.crawling_mode = tk.StringVar(value=TEST_MODE)  # 기본값을 테스트 모드로 설정
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

        # 크롤링 작업을 별도의 스레드에서 실행
        thread = threading.Thread(target=self.crawl_thread, args=(keyword, region, mode))
        thread.start()

    def crawl_thread(self, keyword: str, region: str, mode: str):
        try:
            # GoogleService 인스턴스 생성
            google_service = GoogleService(mode=mode)
            
            # 실제 크롤링 수행
            results = google_service.google_crawling(query=keyword, region=region)
            
            total_results = len(results)
            
            for i, result in enumerate(results):
                # 크롤링 진행 상황에 따라 프로그레스바 업데이트
                progress = int((i + 1) / total_results * 100)
                self.window.after(0, lambda p=progress: self.update_progress(p))
                
                # 현재 처리 중인 항목에 대한 상태 메시지 업데이트
                status_message = f"처리 중: {result.name} ({i+1}/{total_results})"
                self.window.after(0, lambda msg=status_message: self.update_status(msg))

            self.window.after(0, self.finish_crawling)
        except Exception as e:
            error_message = f"크롤링 중 오류 발생: {str(e)}"
            self.window.after(0, lambda msg=error_message: self.update_status(msg))
            self.window.after(0, lambda: self.crawl_button.config(state='normal'))

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

        # 크롤링 시작
        self.crawl_button = ttk.Button(self.main_frame, text="크롤링 시작", command=self.on_crawl)
        self.crawl_button.grid(row=1, column=0, pady=10, sticky='w')

        # 프로그레스 바 추가
        self.progress_bar = ttk.Progressbar(self.main_frame, orient='horizontal', length=200, mode='determinate')
        self.progress_bar.grid(row=1, column=1, columnspan=3, pady=10, padx=(10, 0), sticky='we')

        # 크롤링 모드 라벨
        ttk.Label(self.main_frame, text="크롤링 모드:").grid(row=2, column=0, padx=(0,5), pady=5, sticky='w')

        # 테스트 모드 라디오 버튼
        ttk.Radiobutton(self.main_frame, text=TEST_MODE, 
                        variable=self.crawling_mode, value=TEST_MODE).grid(row=2, column=1, padx=(0,5), pady=5, sticky='w')

        # 데이터 수집 모드 라디오 버튼
        ttk.Radiobutton(self.main_frame, text=GATHER_MODE, 
                        variable=self.crawling_mode, value=GATHER_MODE).grid(row=2, column=2, padx=(0,5), pady=5, sticky='w')

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