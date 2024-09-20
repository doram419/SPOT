from crawling.models import SearchResult

def saveToRDB(data : SearchResult = "저장할 데이터"):
    """
    MySQL DB에 크롤링한 데이터를 저장하고 생성된 pk를 반환해주는 함수

    저장하는 데이터
    - 가게명
    반환 값 
    - pk : int
    """
    # TODO:MySQL에 데이터 생성해서 넣기, 예외처리
    pk = 1
    return pk