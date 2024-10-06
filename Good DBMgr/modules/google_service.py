import googlemaps
from typing import List
from datas.data import Data
from naver_service import NaverService
from api_key import get_key

class GoogleService():
    def __init__(self):
        # Google Maps 클라이언트 초기화 
        self.gmaps = googlemaps.Client(key=get_key("GOOGLE_API_KEY"))
        self.mode = None

    # 구글로 맛집 검색
    def google_crawling(self, query: str = "검색어", 
                        region: str = "지역") -> List[Data]:
        """
        이전 함수명 fetch_top_restaurants_nearby
        """
        places_result = self.gmaps.places(query=f"{region} {query}")

        results = []
        for place in places_result['results']:
            place_id = place.get('place_id', 'None')
            place_details = self.gmaps.place(place_id=place_id, language='ko',
                                        fields=['name', 'url', 'vicinity', 'rating',
                                                'user_ratings_total', 'price_level', 'reviews'])['result']

            name = place_details.get('name', '이름 없음')
            address = place_details.get('vicinity', '주소 없음')
            google_json = place_details

            # 네이버 블로그에서 해당 식당 이름으로 검색한 데이터 가져오기
            blog_datas = NaverService().crawling_naver_blog_data(query=name, region=region)

            results.append(Data(name, address, google_json, blog_datas))
            
        return results

if __name__ == "__main__":
    gs = GoogleService()
    gs.google_crawling("자장면", "서초동")