import tkinter as tk
from tkinter import ttk

class CrawlingModule:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("크롤링 모듈")
        self.window.geometry("600x350")
        self.create_widgets()  # create_widgets 메서드 호출

    def on_crawl(self):
        keyword = self.keyword_entry.get()
        region = self.region_entry.get()

        if len(keyword) >= 1 & len(region) >= 1:
            results = self.start_crawling(keyword, region)
        else:
            print("검색어 또는 지역이 누락되었습니다")

    def start_crawling(self, keyword: str, region: str) -> list:
        """
        크롤링을 해서 돌려주는 함수
        """
        print(f"키워드: {keyword}, 지역: {region}로 크롤링을 시작합니다")    
        return []  # 실제 크롤링 결과를 반환해야 합니다

    def create_widgets(self):
        """
        내부 항목을 추가하는 항목
        """
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.label = ttk.Label(self.main_frame, text="지역:")
        self.label.grid(row=0, column=0, padx=5, pady=5)

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
        self.crawl_button.grid(row=2, column=0, columnspan=2, pady=10)

