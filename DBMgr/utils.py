import googlemaps
from fastapi import HTTPException
from DBMgr.crawling.datas.config import GOOGLE_API_KEY
import re
import googlemaps
from fastapi import HTTPException
from DBMgr.crawling.datas.config import GOOGLE_API_KEY

# Google Maps 클라이언트 초기화
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

# 지역명을 위도/경도로 변환하는 함수
def get_coordinates(region: str):
    geocode_result = gmaps.geocode(region)  # 지역명으로 위도/경도 변환
    if geocode_result and 'geometry' in geocode_result[0]:
        location = geocode_result[0]['geometry']['location']
        return location['lat'], location['lng']  # 위도와 경도를 반환
    else:
        raise HTTPException(status_code=404, detail="해당 지역을 찾을 수 없습니다.")


# HTML 태그를 정규식으로 제거하는 함수
def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def clean_word(raw_word):
    """
    string안에 특정 문자를 제거하는 함수
    :param raw_word: 특정 문자를 제거할 대상 문자열('<' , ',' 제거됨)
    """
    # 쉼표를 공백으로 대체
    cleaned_string = raw_word.replace('>', ' ')
    cleaned_string = cleaned_string.replace(',', ' ')
    
    return cleaned_string

