"""
웹 크롤링을 통해서 Faiss DB셋을 만드는 프로그램
"""
# API 키를 환경변수로 관리하기 위한 설정 파일
from dotenv import load_dotenv
# Langchain 
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from crawling.naver_service import fetch_naver_blog_data
from crawling.google_service import fetch_top_restaurants_nearby
# from openai import OpenAI
import faiss

# API 키 정보 로드
load_dotenv()

def create(region : str = "데이터 크롤링 할 지역",
           keyword : str = "크롤링 할 단어",
        naverSize : int = "네이버 API에서 들고 올 블로그 수",
        googleSize : int = "구글 API에서 들고 올 정보 개수"):
    """
    필요한 데이터를 크롤링 한 다음, Faiss 파일로 만들어주는 함수
    """ 
    # 네이버 API 검색 -> 저장
    # TODO: rating 있는 항목은 값이 들어가지는지 확인해보기
    #naverList = fetch_naver_blog_data(query=keyword, region=region, number=naverSize)
    # print(naverList)

    # 구글 API 검색 -> 저장
    # TODO: 나중에 description에 "google Places 리뷰"만 저장되는 걸 개선하기
    googleList = fetch_top_restaurants_nearby(search_term=keyword,region=region,number=googleSize)

    print(googleList[0])
    # 파싱
    # TODO: description을 파싱하면 좋겠는데 구글은 없기도해
    # vector db 적재

    # vector db 저장
    pass

def delete():
    pass

if __name__ == "__main__":
    create("서초동", "피자집", 10, 10)