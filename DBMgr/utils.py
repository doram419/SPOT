import googlemaps
from fastapi import HTTPException
from config import GOOGLE_API_KEY
import re
import googlemaps
from fastapi import HTTPException
from config import GOOGLE_API_KEY

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

