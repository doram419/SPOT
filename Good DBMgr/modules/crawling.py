import tkinter as tk
from tkinter import ttk

class CrawlingModule:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("크롤링 모듈")
        self.window.geometry("500x350")
        self.create_widgets()  # create_widgets 메서드 호출

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

        # 지역 입력 필드
        self.region_entry = ttk.Entry(self.main_frame)
        self.region_entry.grid(row=0, column=1, padx=5, pady=5)

        # 키워드 라벨과 입력 필드
        ttk.Label(self.main_frame, text="키워드:").grid(row=1, column=0, padx=5, pady=5)
        self.keyword_entry = ttk.Entry(self.main_frame)
        self.keyword_entry.grid(row=1, column=1, padx=5, pady=5)

        # 크롤링 시작 버튼
        self.crawl_button = ttk.Button(self.main_frame, text="크롤링 시작", command=self.on_crawl)
        self.crawl_button.grid(row=2, column=0, columnspan=2, pady=10)

    def on_crawl(self):
        keyword = self.keyword_entry.get()
        region = self.region_entry.get()
        results = self.start_crawling(keyword, region)
