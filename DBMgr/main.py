"""
웹 크롤링을 통해서 Faiss DB셋을 만드는 프로그램
"""
# API 키를 환경변수로 관리하기 위한 설정 파일
from dotenv import load_dotenv
from crawling.google_service import fetch_top_restaurants_nearby
from crud.vectorDB import saveToVDB
from crud.rDB import saveToRDB

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
    # naverList = fetch_naver_blog_data(query=keyword, region=region, number=naverSize)

    # 구글 API 검색 -> 저장
    googleList = fetch_top_restaurants_nearby(search_term=keyword,region=region,number=googleSize)
    save(googleList)

def save(datas : list = "SearchResult list를 주면 DB에 저장하는 함수"):
    """
    크롤링한 데이터를 저장하는 함수
    """

    for data in datas:
        pk = saveToRDB(data=data)
        saveToVDB(data=data, fk=pk)

def delete():
    pass

if __name__ == "__main__":
    create("서초동", "맛집", 0, 3)