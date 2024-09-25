# 모든 크롤링을 시도하여 txt파일로 뽑아내는 코드
from naver_service import crawling_naver_blog_data, crawling_naver_local_data

def start_crawling(keyword : str, region : str):
    result = crawling_naver_blog_data(query=keyword, region=region)
    local = crawling_naver_local_data(query=keyword, region=region)
    result += local
    print("naver local data number : ", len(local))
    print("naver local data number : ", len(result))

if __name__ == "__main__":
    start_crawling(keyword="갈비", region="서초동")