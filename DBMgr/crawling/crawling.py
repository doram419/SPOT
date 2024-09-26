# 모든 크롤링을 시도하여 txt파일로 뽑아내는 코드
from naver_service import crawling_naver_blog_data, crawling_naver_local_data, crawling_naver_web_data
from langchain.text_splitter import RecursiveCharacterTextSplitter

def start_crawling(keyword : str, region : str):
    result = crawling_naver_blog_data(query=keyword, region=region)

if __name__ == "__main__":
    start_crawling(keyword="갈비", region="서초동")