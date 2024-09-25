# 모든 크롤링을 시도하여 txt파일로 뽑아내는 코드
from naver_service import crawling_naver_blog_data

def start_crawling():
    result = crawling_naver_blog_data(query="갈비", region="서초동")
    print("naver blog data number : ", len(result))

if __name__ == "__main__":
    start_crawling()