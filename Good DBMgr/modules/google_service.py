import googlemaps
from typing import List
from datas.data import Data
from naver_service import crawling_naver_blog_data
# from .summarizer import do_summarize

class GoogleService():
    def __init__(self, google_key):
        # Google Maps 클라이언트 초기화 
        self.gmaps = googlemaps.Client(key=google_key)
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
            blog_datas = crawling_naver_blog_data(query=name)
            # description_list.append(f"네이버 블로그 설명: {naver_description}")
            
#         # 리뷰가 있으면 추가
#         reviews = place_details.get('reviews', [])
#         if reviews:
#             review_texts = [review.get('text', '리뷰 내용 없음') for review in reviews]
#             description_list.append(f"리뷰: {' '.join(review_texts)}")

#         # 최종 요약 생성
#         summary = do_summarize(name=place_details.get('name', '이름 없음'), descs=description_list)

#         # Data 객체 생성 및 결과 리스트에 추가
#         results.append(Data(
#             title=place_details.get('name', '이름 없음'),
#             chunked_desc=description_list,  # 결합된 description_list를 chunked_desc에 저장
#             summary=summary,
#             link=place_details.get('url', 'URL 없음')
#         ))
#     return results

if __name__ == "__main__":
    gs = GoogleService('AIzaSyCNnfck488KTdBaPpbrOGz8j0Ncq-y8-Js')
    gs.google_crawling("자장면", "서초동")