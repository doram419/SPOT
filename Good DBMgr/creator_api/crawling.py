from datetime import datetime
import threading
import tkinter as tk
from tkinter import ttk
from .google_service import GoogleService
from .datas.constants import TEST_MODE, GATHER_MODE

class CrawlingModule:
    def __init__(self, parent, status_module):
        self.parent = parent
        self.status_module = status_module
        self.crawling_mode = tk.StringVar(value=TEST_MODE)
        self.create_widgets()
    
    def create_widgets(self):
        self.main_frame = ttk.Frame(self.parent, padding="10")
        
        # 지역 라벨과 입력 필드
        ttk.Label(self.main_frame, text="지역:").grid(row=0, column=0, padx=(0,5), pady=5, sticky='e')
        self.region_entry = ttk.Entry(self.main_frame, width=15)
        self.region_entry.grid(row=0, column=1, padx=(0,15), pady=5, sticky='w')

        # 키워드 라벨과 입력 필드
        ttk.Label(self.main_frame, text="키워드:").grid(row=0, column=2, padx=(0,5), pady=5, sticky='e')
        self.keyword_entry = ttk.Entry(self.main_frame, width=15)
        self.keyword_entry.grid(row=0, column=3, padx=(0,5), pady=5, sticky='w')

        # 크롤링 모드 라벨
        ttk.Label(self.main_frame, text="크롤링 모드:").grid(row=2, column=0, padx=(0,5), pady=5, sticky='w')

        # 테스트 모드 라디오 버튼
        ttk.Radiobutton(self.main_frame, text=TEST_MODE, 
                        variable=self.crawling_mode, value=TEST_MODE).grid(row=2, column=1, padx=(0,5), pady=5, sticky='w')

        # 데이터 수집 모드 라디오 버튼
        ttk.Radiobutton(self.main_frame, text=GATHER_MODE, 
                        variable=self.crawling_mode, value=GATHER_MODE).grid(row=2, column=2, padx=(0,5), pady=5, sticky='w')

    async def start_crawling(self, keyword: str, region: str, mode: str):
        """
        크롤링을 시작하는 함수
        """
        self.status_module.update_status(f"키워드: {keyword}, 지역: {region}, 모드: {mode}(으)로 크롤링을 시작합니다")
        
        try:
            google_service = GoogleService(mode=mode)
            results = await google_service.google_crawling(query=keyword, region=region)
            
            total_results = len(results)
            
            for i, result in enumerate(results):
                progress = int((i + 1) / total_results * 100)
                
                status_message = f"처리 중: {result.name} ({i+1}/{total_results})"
                self.status_module.update_status(status_message)

            self.status_module.update_status("크롤링이 완료되었습니다.")
            return results
        except Exception as e:
            error_message = f"크롤링 중 오류 발생: {str(e)}"
            self.status_module.update_status(error_message)
            return None

    def get_widget(self):
        return self.main_frame