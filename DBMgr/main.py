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

    create(region="서울", keyword="분위기가 완전 좋은 곳을 찾아줘. 난 내 대화소리가 유출되는 걸 싫어하기 때문에 매장이 좀 넓었으면 좋겠어. 하지만 너무 시끄러운 술집은 싫어. 조명이 노란빛이어서 얼굴이 예뻐보일 수 있는 술집이라면 더 좋겠어. 메뉴는 칵테일이나 위스키를 다뤘으면 좋겠어. 두 명이서 6만원이면 충분히 술과 안주를 즐길 수 있는 곳이었으면 좋겠어. 어떤 남자든 꼬실 수 있는 최고의 분위기 술집을 찾아줘. 서울 내에 있는 술집이어야해.", naverSize=0, googleSize=100)

    # 지금 테스트 중

    result = searchVDB(query="회", search_amount=3)
    print(f"vdb 검색 쿼리 : 회")
    if result:
        for r in result:
            print(f"{r['title']} : {r['link']}")
    else:
        print("검색 결과가 없습니다.")



