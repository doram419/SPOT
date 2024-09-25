import googlemaps
from typing import List
from models import SearchResult
from config import GOOGLE_API_KEY

# Google Maps 클라이언트 초기화
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

# 입력한 지역(동/역)을 기반으로 좌표(위도, 경도)를 가져오는 함수
def get_location_from_region(region: str):
    geocode_result = gmaps.geocode(region)
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        return location['lat'], location['lng']
    return None, None

# 반경 1km 내에서 상위 5개의 맛집 검색 
def fetch_top_restaurants_nearby(search_term: str = "검색어", region: str = "지역", 
                                 number : int = "가져올 개수") -> List[SearchResult]:
    # 입력한 검색어를 기반으로 좌표를 가져옴
    # 위도, 경도
    lat, lng = get_location_from_region(region)
    if lat is None or lng is None:
        print(f"입력한 지역 '{region}'에 대한 좌표를 찾을 수 없습니다.")
        return []

    # 위도와 경도를 기반으로 반경 1km 내에서 맛집 검색
    places_result = gmaps.places_nearby(location=(lat, lng), radius=1000, keyword=search_term)

    results = []
    for place in places_result['results']:
        # 주변 검색 결과로 가져올 수 없는 항목은 id를 통해 장소 검색으로 가져오기
        place_id = place.get('place_id', 'None')
        place_details = gmaps.place(place_id=place_id, language='ko',
                                    fields=['name', 'url', 'vicinity', 'rating',
                   'user_ratings_total', 'price_level', 'reviews', 'serves_beer',
                   'serves_wine', 'serves_breakfast', 'serves_brunch', 'serves_lunch',
                   'serves_dinner', 'serves_vegetarian_food', 'takeout'])['result']
        
        # api 효율화를 위해서 필요한 필드만 가져와서 결과에 append
        results.append(SearchResult(
            title=place_details.get('name', None),
            link=place_details.get('url', None), 
            address=place_details.get('vicinity', None),
            reviews=place_details.get('reviews', None),
            description=place_details.get('editorial_summary', None),
            google_id=place_id,
            rating=place_details.get('rating', 0.0),
            views=place_details.get('user_ratings_total', 0),
            price_level=place_details.get('price_level', 0),
            serves_beer=place_details.get('serves_beer', False),
            serves_wine=place_details.get('serves_wine', False),
            serves_breakfast=place_details.get('serves_breakfast', False),
            serves_brunch=place_details.get('serves_brunch', False),
            serves_lunch=place_details.get('serves_lunch', False),
            serves_dinner=place_details.get('serves_dinner', False),
            serves_vegetarian_food=place_details.get('serves_vegetarian_food', False),
            takeout=place_details.get('takeout', False),
            international_phone_number=place_details.get('international_phone_number', '전화 번호 없음')
        ))

    # 평점과 리뷰 수를 기준으로 정렬 후 상위 5개 반환
    return sorted(results, key=lambda x: (x.rating, x.views), reverse=True)[:number]
