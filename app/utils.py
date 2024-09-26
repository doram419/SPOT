
import re
import googlemaps
from fastapi import HTTPException
from app.config import GOOGLE_API_KEY
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 비밀번호 해싱
def hash_password(password: str):
    return pwd_context.hash(password)

# 비밀번호 검증
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# JWT 토큰 생성
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# JWT 토큰 검증
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise JWTError("토큰에 사용자 정보가 없습니다.")
        return username
    except JWTError:
        raise JWTError("유효하지 않은 토큰입니다.")

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
