from fastapi import APIRouter, Request, Form, HTTPException  # FastAPI에서 APIRouter, Request, Form 및 예외처리 기능을 가져옴
from fastapi.responses import HTMLResponse  # HTML 응답을 처리하는 HTMLResponse를 가져옴
from fastapi.templating import Jinja2Templates  # Jinja2 템플릿을 사용하여 HTML 파일을 렌더링하기 위해 가져옴
from app.crawling.google_service import fetch_top_restaurants_nearby  # 구글 맛집 데이터 가져오는 함수
from app.crawling.naver_service import fetch_naver_blog_data  # 네이버 블로그 데이터 가져오는 함수
from app.bert_service import get_embedding  # 텍스트 임베딩을 생성하는 함수
import faiss  # 벡터 검색 및 임베딩을 위한 라이브러리 FAISS
import numpy as np  # Numpy는 벡터 및 배열 계산을 위한 라이브러리
from transformers import pipeline  # Hugging Face의 Transformers 모델을 위한 파이프라인
import re  # 정규식을 사용하여 텍스트 패턴을 추출하는 라이브러리

from transformers import AutoTokenizer, AutoModelForTokenClassification  # KoELECTRA 모델을 위한 토크나이저 및 분류 모델 가져옴

# KoELECTRA 모델을 이용한 NER 파이프라인
tokenizer = AutoTokenizer.from_pretrained("monologg/koelectra-base-v3-discriminator")  # KoELECTRA 토크나이저 로드
model = AutoModelForTokenClassification.from_pretrained("monologg/koelectra-base-v3-discriminator")  # KoELECTRA NER 모델 로드

# NER 파이프라인 생성
ner_model = pipeline("ner", model=model, tokenizer=tokenizer)  # NER 태스크를 위한 파이프라인 생성

# FAISS 인덱스 초기화 (L2 거리 기반 인덱스)
dimension = 768  # 벡터 차원 수 (BERT 임베딩 차원)
index = faiss.IndexFlatL2(dimension)  # L2 거리 기반 FAISS 인덱스 생성


# 벡터 저장 함수
def store_vectors_in_faiss(vectors: np.ndarray):
    if len(vectors.shape) > 2:  # 벡터 차원이 2차원이 아닐 경우
        vectors = np.squeeze(vectors)  # 불필요한 차원을 제거하여 2차원으로 만듦
    if len(vectors.shape) != 2 or vectors.shape[1] != dimension:  # 벡터의 차원이 2차원이 아니거나 벡터 차원이 맞지 않을 경우
        raise ValueError(f"벡터의 차원이 올바르지 않습니다. 예상: 2D 배열 [{None}, {dimension}], 받은: {vectors.shape}")  # 오류 발생
    index.add(vectors)  # FAISS 인덱스에 벡터 추가


# 사전 정의된 한국 주요 지역명 리스트 (필요시 확장 가능)
korean_locations = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]  # 한국의 주요 지역명 리스트


# 정규식을 사용한 지역 추출 함수
def extract_location_with_regex(text: str):
    # ~역 또는 ~동 패턴 추출
    loc_patterns = re.findall(r'\w+역|\w+동', text)  # 텍스트에서 "역", "동"으로 끝나는 단어 추출

    # 사전에 정의된 지역명 추출
    for location in korean_locations:  # 미리 정의된 지역 리스트에서
        if location in text:  # 지역명이 텍스트에 포함되어 있으면
            loc_patterns.append(location)  # 지역 패턴 리스트에 추가

    return loc_patterns  # 지역명 리스트 반환


# NER과 정규식을 병행해서 지역과 키워드 추출
def extract_entities(text: str):
    # NER 추출
    entities = ner_model(text)  # NER 모델을 사용하여 텍스트에서 개체명 추출
    print(f"NER 결과: {entities}")  # 추출된 NER 결과 출력

    locations = []  # 지역명 저장 리스트
    keywords = []  # 키워드 저장 리스트

    # 정규식을 사용한 지역명 추출
    regex_locations = extract_location_with_regex(text)  # 정규식을 사용해 지역명 추출
    locations.extend(regex_locations)  # 추출된 지역명을 지역 리스트에 추가

    # NER 결과에서 단어 추출
    for entity in entities:  # NER 모델에서 추출된 개체들에 대해
        word = entity['word'].replace('##', '')  # WordPiece 토크나이저가 분할한 토큰의 "##" 제거
        if entity['entity'] == 'LOC':  # NER 결과에서 지역으로 추출된 항목
            locations.append(word)  # 지역명 리스트에 추가
        else:
            keywords.append(word)  # 키워드 리스트에 추가

    return locations, keywords  # 지역명과 키워드 반환


# FastAPI의 APIRouter 인스턴스 생성
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")  # Jinja2 템플릿 경로 설정


# GET 요청 처리, 메인 페이지 렌더링
@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})  # "index.html" 템플릿을 렌더링하여 반환


# POST 요청을 통해 검색을 처리하는 엔드포인트
@router.post("/search/", response_class=HTMLResponse)
async def search_restaurant(request: Request, search_input: str = Form(...)):  # 사용자가 제출한 검색어를 Form 데이터로 받음
    if not search_input:  # 검색어가 비어 있을 경우
        raise HTTPException(status_code=400, detail="검색어를 입력하세요.")  # 400 Bad Request 에러 반환

    print(f"검색어: {search_input}")  # 입력된 검색어 출력

    # NER 및 정규식을 사용하여 지역(LOC) 및 키워드 추출
    locations, keywords = extract_entities(search_input)  # NER과 정규식을 이용해 지역 및 키워드 추출

    print(f"추출된 지역: {locations}, 추출된 키워드: {keywords}")  # 추출된 지역과 키워드 출력

    if not locations:  # 지역이 추출되지 않았을 경우
        region = "서울"  # 기본 지역을 서울로 설정
        query = search_input  # 전체 검색어를 쿼리로 사용
    else:
        region = locations[0]  # 첫 번째 추출된 지역을 지역으로 설정
        query = ' '.join(keywords) if keywords else search_input  # 추출된 키워드를 쿼리로 사용

    # 네이버 블로그 및 구글 맛집 데이터 가져오기
    naver_results = fetch_naver_blog_data(query, region, keywords)  # 네이버 블로그 검색 결과 가져옴
    google_results = fetch_top_restaurants_nearby(query, region)  # 구글 맛집 검색 결과 가져옴

    combined_results = naver_results + google_results  # 네이버와 구글 결과를 합침

    # 임베딩 벡터 생성 (결과에 대한 임베딩 처리)
    embeddings = np.array([get_embedding(result.title + " " + result.description) for result in combined_results],
                          dtype='float32')  # 검색 결과에 대해 임베딩 생성

    if embeddings.ndim == 3:  # 임베딩 차원이 3차원일 경우
        embeddings = embeddings.reshape(-1, dimension)  # 2차원으로 변환
    elif embeddings.ndim == 2:  # 이미 2차원일 경우 그대로 사용
        embeddings = embeddings
    elif embeddings.ndim == 1:  # 1차원일 경우
        embeddings = embeddings.reshape(1, dimension)  # 2차원으로 변환

    store_vectors_in_faiss(embeddings)  # FAISS 인덱스에 벡터 저장

    # 검색 결과를 렌더링하여 반환
    return templates.TemplateResponse("index.html", {
        "request": request,
        "search_results": combined_results  # 검색 결과를 템플릿에 전달
    })
