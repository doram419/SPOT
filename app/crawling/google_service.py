import googlemaps
from typing import List
from app.models import SearchResult
from app.config import GOOGLE_API_KEY

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
def fetch_top_restaurants_nearby(search_term: str = "검색어", region: str = "지역") -> List[SearchResult]:
    # 입력한 검색어를 기반으로 좌표를 가져옴
    # 위도, 경도
    lat, lng = get_location_from_region(region)
    if lat is None or lng is None:
        print(f"입력한 지역 '{region}'에 대한 좌표를 찾을 수 없습니다.")
        return []

    # 위도와 경도를 기반으로 반경 1km 내에서 맛집 검색
    places_result = gmaps.places_nearby(location=(lat, lng), radius=1000, keyword=search_term)

    results = []
    for place in places_result.get('results', []):
        place_id = place.get('place_id')
        place_details = gmaps.place(place_id=place_id, fields=['name', 'rating', 'user_ratings_total', 'url'])

        if place_details:
            place_name = place_details['result'].get('name', 'N/A')
            place_url = place_details['result'].get('url', '#')
            place_rating = place_details['result'].get('rating', 0)
            reviews_total = place_details['result'].get('user_ratings_total', 0)

            results.append(SearchResult(
                title=place_name,
                link=place_url,
                description="Google Places 리뷰",
                rating=place_rating,
                views=reviews_total
            ))

    # 평점과 리뷰 수를 기준으로 정렬 후 상위 5개 반환
    return sorted(results, key=lambda x: (x.rating, x.views), reverse=True)[:5]
