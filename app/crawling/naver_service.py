import requests
from urllib import parse
import re
from typing import List
from app.models import SearchResult
from app.utils import clean_html
from app.config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

# 네이버 블로그 데이터 조회수 높은 순으로 5개 가져오기
def fetch_naver_blog_data(query: str, region: str, keywords: List[str]) -> List[SearchResult]:
    try:
        # 지역과 검색어를 섞어서 검색
        # TODO : 검색어라는 단어로밖에 검색이 안돼나? quote에 대해 알아보자
        combined_query = f"{region} {query}"
        enc_text = parse.quote(combined_query)
        url = f"https://openapi.naver.com/v1/search/blog?query={enc_text}"

        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }

        # 네이버 블로그 API 호출
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        items = response.json().get("items", [])
        results = []

        # 각 블로그 항목에 대해 키워드가 포함된 것만 필터링
        for item in items:
            title = clean_html(item['title'])
            description = clean_html(item['description'])

            # 키워드가 블로그 제목이나 내용에 포함되어 있는지 확인
            if any(keyword in title or keyword in description for keyword in keywords):
                # 블로그 게시글 조회수(여기서는 postdate가 대신 사용됨)와 함께 결과 리스트에 추가
                post_date = int(re.search(r'\d+', item.get('postdate', '0')).group())
                results.append(SearchResult(
                    title=title,
                    link=item['link'],
                    description=description,
                    views=post_date  # 조회수를 대신할 값이 없으므로 postdate 사용
                ))

        # 조회수 순으로 정렬 후 상위 5개 반환
        return sorted(results, key=lambda x: x.views, reverse=True)[:5]

    except requests.exceptions.RequestException as e:
        print(f"Naver API 요청 실패: {str(e)}")
        return []
    except Exception as e:
        print(f"네이버 블로그 데이터를 처리하는 중 오류가 발생했습니다: {str(e)}")
        return []
