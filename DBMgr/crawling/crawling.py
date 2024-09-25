# 모든 크롤링을 시도하여 txt파일로 뽑아내는 코드
from naver_service import crawling_naver_blog_data, crawling_naver_local_data, crawling_naver_web_data
from langchain.text_splitter import RecursiveCharacterTextSplitter
from datetime import datetime

def start_crawling(keyword : str, region : str):
    result = crawling_naver_blog_data(query=keyword, region=region)
    local = crawling_naver_local_data(query=keyword, region=region)
    result += local
    web = crawling_naver_web_data(query=keyword, region=region)
    result += web

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)

    splits = text_splitter.split_documents(result)

    # 파일에 리스트를 저장
    file_name = "data_"

    now = datetime.now()
    # 현재 시간을 timestamp로 변환 (float 형식)
    timestamp = now.timestamp()

    # 정수형으로 변환 (소수점 제거)
    timestamp_int = int(timestamp)
    extra_name = timestamp_int

    print(file_name + str(timestamp) + ".txt")
    # with open('my_list.txt', 'w') as file:
    #     file.write(', '.join(my_list))  # 리스트의 항목을 쉼표로 구분해 한 줄로 저장

if __name__ == "__main__":
    start_crawling(keyword="갈비", region="서초동")