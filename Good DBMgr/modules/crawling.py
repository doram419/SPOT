import tkinter as tk
from tkinter import ttk
from .window_utils import position_window

class CrawlingModule:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("크롤링 모듈")
        self.window.geometry("600x400")
        self.create_widgets()
        
        # 창 크기를 위젯에 맞게 조절
        self.window.update()
        self.window.geometry('')

        # 부모 창의 오른쪽에 크롤링 창 배치
        position_window(self.parent, self.window)

    def on_crawl(self):
        keyword = self.keyword_entry.get()
        region = self.region_entry.get()

        if len(keyword) >= 1 and len(region) >= 1:
            results = self.start_crawling(keyword, region)
        else:
            self.update_status("검색어 또는 지역이 누락되었습니다")

    def start_crawling(self, keyword: str, region: str) -> list:
        """
        크롤링을 해서 돌려주는 함수
        """
        message = f"키워드: {keyword}, 지역: {region}(으)로 크롤링을 시작합니다\n"
        self.update_status(message)
        return []  # 실제 크롤링 결과를 반환해야 합니다

    def update_status(self, message: str):
        """
        상태 텍스트 필드를 업데이트하는 함수
        """
        self.status_text.config(state='normal')
        # self.status_text.delete('1.0', tk.END)
        self.status_text.insert(tk.END, message)
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

        # 크롤링 시작 버튼 (x좌표를 조정하여 라벨의 시작점과 일치시킴)
        self.crawl_button = ttk.Button(self.main_frame, text="크롤링 시작", command=self.on_crawl)
        self.crawl_button.grid(row=1, column=0, columnspan=2, pady=10, sticky='w')

        # 현재 상태 라벨
        ttk.Label(self.main_frame, text="현재 상태:").grid(row=2, column=0, padx=(0,5), pady=5, sticky='nw')

        # 상태를 표시할 읽기 전용 텍스트 필드
        self.status_text = tk.Text(self.main_frame, height=5, width=50, state='disabled')
        self.status_text.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky='nsew')

        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(self.main_frame, orient='vertical', command=self.status_text.yview)
        scrollbar.grid(row=3, column=4, sticky='ns')
        self.status_text['yscrollcommand'] = scrollbar.set

        # 그리드 설정을 조정하여 텍스트 필드가 창 크기에 맞춰 확장되도록 함
        self.main_frame.columnconfigure(3, weight=1)
        self.main_frame.rowconfigure(3, weight=1)