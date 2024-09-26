# 모든 크롤링을 시도하여 txt파일로 뽑아내는 코드
from naver_service import crawling_naver_blog_data
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils import clean_html
from datas.data import Data
from summarizer import summarize_desc
from langchain.schema import Document  # 문서 객체가 필요하다면 임포트

def start_crawling(keyword : str, region : str):
    """
    네이버 블로그에서 크롤링을 해서 돌려주는 함수
    """
    result = crawling_naver_blog_data(query=keyword, region=region)
    
    return result

def make_datas(datas : list):
    """
    가져온 정보들을 Class Data로 바꿔주는 함수
    """
    result = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
    for d in datas:
        title=clean_html(d['title'])
        doc=Document(page_content=d['description']) 
        first = d['description'][0]

        result.append(Data(
            title=title, 
            chunked_desc=text_splitter.split_documents([doc]), 
            summary=summarize_desc(restaurant_name=title, descs=first)))

    return result

if __name__ == "__main__":
    infos = start_crawling(keyword="갈비", region="서초동")
    infos = make_datas(infos)
    print(infos)