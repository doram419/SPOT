import requests
from urllib import parse
from typing import List
from datas.naver_data import NaverData

class NaverService():
    def __init__(self, key, secret) -> None:
        self.naver_key = key
        self.naver_secret = secret

    def crawling_naver_blog_data(self,
            query: str = "검색할 가게명", region :str = "검색할 지명", 
            display: int = 10) -> list[NaverData]:
        """
        네이버 블로그 데이터 최대한 많이 (최대100개) 가져오기
        display : 한 구글 지역에 매칭될 수량 10~100
        """
        try:
            # 지역과 검색어를 결합하여 검색
            combined_query = f"{region} {query}"
            enc_text = parse.quote(combined_query)
            base_url = "https://openapi.naver.com/v1/search/blog.json"

            headers = {
                "X-Naver-Client-Id": self.naver_key,
                "X-Naver-Client-Secret": self.naver_secret
            }

            start = 1
            sort = "sim"

            url = f"{base_url}?query={enc_text}&display={display}&start={start}&sort={sort}"

            # 네이버 블로그 API 호출
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            print(response)

            items = response.json().get("items", [])
            # if items:
            #     description = items[0].get('description', '네이버 블로그 설명 없음')
            #     return description
            # else:
            #     return "설명 없음"

        except requests.exceptions.RequestException as e:
            print(f"Naver API 요청 실패: {str(e)}")
            return "네이버 블로그 설명 오류"