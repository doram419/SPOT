import requests
import urllib.parse
import re
import googlemaps
import openai
import torch
from app.models import SearchResult
from app.utils import clean_html, get_coordinates
from typing import List
from app.config import OPENAI_API_KEY, GOOGLE_API_KEY, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
from app.models_loader import tokenizer, bert_model

# BERT 임베딩 생성 함수
def get_embedding(text: str):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = bert_model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).numpy()

# 긴 문장을 청크로 나누는 함수
def chunk_text(text: str, chunk_size=512):
    tokens = tokenizer.tokenize(text)  # BERT 토크나이저로 토큰화
    return [' '.join(tokens[i:i + chunk_size]) for i in range(0, len(tokens), chunk_size)]

# OpenAI GPT로 키워드 추출
def extract_keywords(text: str):
    chunks = chunk_text(text)
    keywords = []

    # 각 청크에 대해 GPT 모델을 사용하여 키워드 추출
    for chunk in chunks:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts keywords."},
                {"role": "user", "content": f"Extract keywords from the following text: {chunk}"}
            ]
        )
        keywords.append(response['choices'][0]['message']['content'].strip())

    return ' '.join(keywords)

# Google Maps 클라이언트 초기화
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

# OpenAI API 키 설정
openai.api_key = OPENAI_API_KEY

# Google Places API에서 리뷰가 많고 평점이 좋은 장소 5개 검색
def fetch_google_places(query: str, region: str) -> List[SearchResult]:
    lat, lng = get_coordinates(region)
    places_result = gmaps.places_nearby(location=(lat, lng), radius=1000, keyword=query)

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

    return sorted(results, key=lambda x: (x.views, x.rating), reverse=True)[:5]

# 네이버 블로그 데이터 조회수 높은 순으로 5개 가져오기
def fetch_naver_blog_data(query: str, region: str, keywords: List[str]) -> List[SearchResult]:
    try:
        enc_text = urllib.parse.quote(query)
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