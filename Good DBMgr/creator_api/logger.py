import logging
import os
from datetime import datetime

class LoggingModule:
    def __init__(self, log_dir="./logs"):
        self.log_dir = log_dir
        self.logger = None
        self.setup_logging()

    def setup_logging(self):
        os.makedirs(self.log_dir, exist_ok=True)
        log_file = os.path.join(self.log_dir, f"vdb_creation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        self.logger = logging.getLogger('VdbCreation')
        self.logger.setLevel(logging.INFO)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)

    def log_vdb_creation(self, keyword, region, mode, chunk_size, overlap, embedding_model, embedding_version):
        log_message = f"""
        VDB 생성 완료:
        - 키워드: {keyword}
        - 지역: {region}
        - 모드: {mode}
        - 청킹 사이즈: {chunk_size}
        - 오버랩: {overlap}
        - 임베딩 모델: {embedding_model}
        - 임베딩 버전: {embedding_version}
        """
        self.logger.info(log_message)

    def log_error(self, error_message):
        self.logger.error(f"VDB 생성 중 오류 발생: {error_message}")

    def log_info(self, message):
        self.logger.info(message)