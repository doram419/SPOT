"""
웹 크롤링을 통해서 Faiss DB를 만드는 프로그램
"""
# API 키를 환경변수로 관리하기 위한 설정 파일
from dotenv import load_dotenv
from vectorMgr import saveToVDB, searchVDB
from crawling.crawling import start_crawling, make_datas

user_input = int()

# API 키 정보 로드
load_dotenv()

def find(region : str = "데이터 크롤링 할 지역",
         keyword : str = "크롤링 할 단어"):
    """
    정보를 찾고, 데이터를 만들어주는 함수
    """
    infos = start_crawling(keyword=keyword, region=region)
    infos = make_datas(infos)
    # 유저에게 뭘 표현해줄 것인가?
    return infos

def save(datas : list = "SearchResult list를 주면 DB에 저장하는 함수"):
    """
    크롤링한 데이터를 저장하는 함수
    """
    for data in datas:
        saveToVDB(data=data)

if __name__ == "__main__":
    # find(keyword="갈비", region="서초동")
    # 크롤링 및 저장
    # save(datas=find(keyword="맛집", region="서초동"))

    result = searchVDB(query="냉면", search_amount=3)



