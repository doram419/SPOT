from typing import Optional

class Raw_data():
    """
    크롤링한 데이터에서 txt를 뽑아내서 원문을 저장하는 클래스
    
    """
    name : str
    address : str
    road_address : Optional[str]
    # 이름과 주소가 같다면 동일한 가게일 것이다
    content : list
    # 그 가게에 대한 정보는 가리지 않고 list로 때려넣자
    # 그 다음 meta와 context로 나누자
    