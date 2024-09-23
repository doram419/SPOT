"""
웹 크롤링을 통해서 Faiss DB셋을 만드는 프로그램
"""
# API 키를 환경변수로 관리하기 위한 설정 파일
from dotenv import load_dotenv
from google_service import fetch_top_restaurants_nearby
from vectorDB import saveToVDB, searchVDB
from rDB import saveToRDB

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

def show():
    pass

if __name__ == "__main__":
    # 서초동에 있는 맛집 데이터를 google api를 통해서 찾아오고 vdb로 저장하는 코드
    # TODO: 인터페이스 만들기
    create(region="서초동", keyword="맛집", naverSize=0, googleSize=20)

    # 지금 테스트 중
    result = searchVDB(query="회", search_amount=3)
    for r in result:
        print(f"{r['title']} : {r['link']}")

