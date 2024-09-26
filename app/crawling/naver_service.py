import requests
from urllib import parse
import re
from typing import List
from app.models import SearchResult
from app.utils import clean_html
from app.config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET


# 지역 필터링 함수: 지역명이 제목 또는 설명에 포함된 블로그만 반환
def filter_by_region(items: List[dict], region: str) -> List[dict]:
    filtered_items = []

    for item in items:
        title = clean_html(item['title'])
        description = clean_html(item['description'])

        # 지역명이 제목 또는 설명에 포함되어 있는지 확인
        if region in title or region in description:
            filtered_items.append(item)

    return filtered_items


# 네이버 블로그 최신 데이터와 유사한 블로그 데이터를 검색
def fetch_naver_blog_data(query: str, region: str, keywords: List[str]) -> List[SearchResult]:
    try:
        combined_query = f"{region} {query}"  # 지역과 검색어 결합
        enc_text = parse.quote(combined_query)
        url = f"https://openapi.naver.com/v1/search/blog?query={enc_text}"

        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        items = response.json().get("items", [])

        # 지역 필터링 적용
        filtered_items = filter_by_region(items, region)

        results = []
        for item in filtered_items:
            title = clean_html(item['title'])
            description = clean_html(item['description'])

            # 키워드가 제목이나 내용에 포함된 항목만 필터링
            if any(keyword in title or keyword in description for keyword in keywords):
                post_date = int(re.search(r'\d+', item.get('postdate', '0')).group())
                results.append(SearchResult(
                    title=title,
                    link=item['link'],
                    description=description,
                    views=post_date
                ))

        return sorted(results, key=lambda x: x.views, reverse=True)[:5]

    except requests.exceptions.RequestException as e:
        print(f"Naver API 요청 실패: {str(e)}")
        return []
    except Exception as e:
        print(f"네이버 블로그 데이터를 처리하는 중 오류가 발생했습니다: {str(e)}")
        return []
