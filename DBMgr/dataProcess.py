from models import SearchResult

def process(crawlingData : SearchResult):
    """
    데이터 유효성을 검사해서 db에 넣을 수 있는 형태로 만들어주는 함수
    """
    processed_data = crawlingData

    if processed_data.title == None:
        processed_data.title = '이름 없음'
    if processed_data.link == None:
        processed_data.link = 'url 없음'
    if processed_data.address == None:
        processed_data.address = '주소 없음'
    if processed_data.reviews == None:
        processed_data.reviews = ['리뷰 없음']
    if processed_data.description == None:
        processed_data.description = '설명 없음'
    if processed_data.menus == None:
        processed_data.menus = ['메뉴 없음']
    if processed_data.category == None:
        processed_data.category = '카테고리 없음'
    if processed_data.rating == None:
        processed_data.rating = 0.0
    if processed_data.views == None:
        processed_data.views = 0
    if processed_data.price_level == None:
        processed_data.price_level = 0
    if processed_data.google_id == None:
        processed_data.google_id = '구글 id 없음'
    if processed_data.serves_beer == None:
        processed_data.serves_beer = False
    if processed_data.serves_wine == None:
        processed_data.serves_wine = False
    if processed_data.serves_breakfast == None:
        processed_data.serves_breakfast = False
    if processed_data.serves_brunch == None:
        processed_data.serves_brunch = False
    if processed_data.serves_lunch == None:
        processed_data.serves_lunch = False
    if processed_data.serves_dinner == None:
        processed_data.serves_dinner = False
    if processed_data.serves_vegetarian_food == None:
        processed_data.serves_vegetarian_food = False
    if processed_data.takeout == None:
        processed_data.takeout = False
    if processed_data.international_phone_number == None:
        processed_data.international_phone_number = "전화 번호 없음"

    return processed_data