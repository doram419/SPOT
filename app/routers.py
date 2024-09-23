# 필요한 라이브러리 임포트
from fastapi import APIRouter, Request, Form, HTTPException  # FastAPI의 핵심 기능들
from fastapi.responses import HTMLResponse  # HTML 응답을 위한 클래스
from fastapi.templating import Jinja2Templates  # Jinja2 템플릿 렌더링
from app.crawling.google_service import fetch_top_restaurants_nearby  # 구글 맛집 데이터 크롤링 함수
from app.crawling.naver_service import fetch_naver_blog_data  # 네이버 블로그 데이터 크롤링 함수
from app.bert_service import get_embedding  # 텍스트 임베딩 생성 함수 (BERT 기반)
import faiss  # 벡터 검색을 위한 라이브러리 (FAISS)
import numpy as np  # 수치 계산을 위한 Numpy
import re  # 정규식을 위한 라이브러리

# Hugging Face Transformers 모델 관련 라이브러리 임포트
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# 사전 학습된 BERT 모델과 토크나이저 불러오기
tokenizer = AutoTokenizer.from_pretrained("kykim/bert-kor-base")
model = AutoModelForTokenClassification.from_pretrained("kykim/bert-kor-base")

# NER(Named Entity Recognition) 모델 생성 (단어 단위 NER을 위한 파이프라인)
ner_model = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

# 임의의 임베딩 벡터 생성 (FAISS에서 벡터 검색을 테스트하기 위한 데이터)
dimension = 768  # BERT 모델의 임베딩 벡터 차원 (768차원)
vectors = np.random.rand(100, dimension).astype('float32')  # 100개의 임의 벡터 생성

# FAISS 인덱스 생성 및 임베딩 벡터 추가 (벡터 기반 검색을 위한 인덱스 생성)
index = faiss.IndexFlatL2(dimension)  # L2 거리 기반 인덱스 생성
index.add(vectors)  # 임베딩 벡터를 인덱스에 추가


# 벡터를 FAISS 인덱스에 저장하는 함수
def store_vectors_in_faiss(vectors: np.ndarray):
    # 벡터가 비어 있는지 확인
    if vectors.size == 0:
        raise ValueError("벡터 배열이 비어 있습니다. 벡터를 추가할 수 없습니다.")

    # 벡터의 차원을 조정 (벡터가 2D 배열인지 확인)
    if len(vectors.shape) > 2:
        vectors = np.squeeze(vectors)  # 3D 이상일 경우 차원 축소
    if len(vectors.shape) != 2 or vectors.shape[1] != dimension:
        # 벡터의 차원이 2D인지, 두 번째 차원이 BERT 벡터의 차원과 일치하는지 확인
        raise ValueError(f"벡터의 차원이 올바르지 않습니다. 예상: 2D 배열 [{None}, {dimension}], 받은: {vectors.shape}")

    index.add(vectors)  # FAISS 인덱스에 벡터 추가


# 한국 주요 지역명 리스트 (NER 또는 정규식으로 추출할 수 없는 경우를 대비하여 사용)
korean_locations = [
    "서울", "부산", "대구", "인천", "광주", "대전", "울산",
    "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"
]

# 정규식을 사용하여 텍스트에서 지역명 추출 (예: '서울역', '강남구' 등)
def extract_location_with_regex(text: str):
    loc_patterns = re.findall(r'\w+역|\w+동|\w+시|\w+구|\w+군', text)  # '역', '동', '시', '구', '군' 패턴 찾기

    # 사전 정의된 한국 지역명과 일치하는지 확인하고 일치하는 지역을 리스트에 추가
    for location in korean_locations:
        if location in text:
            loc_patterns.append(location)

    return loc_patterns  # 추출된 지역 리스트 반환


# NER과 정규식을 병행하여 텍스트에서 지역명(LOC)과 키워드 추출
def extract_entities(text: str):
    # NER 모델을 사용하여 엔터티 추출
    entities = ner_model(text)
    print(f"NER 결과: {entities}")

    locations = []  # 지역명 저장
    keywords = []   # 키워드 저장

    # 정규식으로 추출한 지역명을 리스트에 추가
    regex_locations = extract_location_with_regex(text)
    locations.extend(regex_locations)

    # NER 결과에서 엔터티를 추출하여 분류
    for entity in entities:
        word = entity['word']
        entity_label = entity.get('entity_group', '')  # 엔터티 그룹이 없는 경우 기본값으로 빈 문자열 설정

        # LOC(위치) 관련 엔터티인 경우 지역으로 처리
        if 'LOC' in entity_label or 'GPE' in entity_label:
            locations.append(word)
        else:
            # 그 외 엔터티는 키워드로 처리
            keywords.append(word)

    # 만약 NER에서 지역을 추출하지 못했으면 정규식 결과를 사용
    if not locations and regex_locations:
        locations = regex_locations

    # 중복 제거 후 결과 반환
    locations = list(set(locations))
    keywords = list(set(keywords))

    return locations, keywords  # 지역과 키워드 반환



# FastAPI의 APIRouter 인스턴스 생성
router = APIRouter()  # API 경로를 관리하는 라우터
templates = Jinja2Templates(directory="app/templates")  # Jinja2 템플릿 디렉토리 설정


# GET 요청 처리, 메인 페이지 렌더링
@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # 메인 페이지 템플릿 렌더링
    return templates.TemplateResponse("index.html", {"request": request})


# POST 요청을 통해 검색을 처리하는 엔드포인트
@router.post("/search/", response_class=HTMLResponse)
async def search_restaurant(request: Request, search_input: str = Form(...)):
    # 검색어가 없으면 예외 발생
    if not search_input:
        raise HTTPException(status_code=400, detail="검색어를 입력하세요.")

    print(f"검색어: {search_input}")

    # NER과 정규식을 사용하여 텍스트에서 지역과 키워드 추출
    locations, keywords = extract_entities(search_input)
    print(f"추출된 지역: {locations}, 추출된 키워드: {keywords}")

    # 추출된 지역이 없으면 기본 지역(서울) 설정
    if not locations:
        region = "서울"  # 기본 지역
        query = search_input  # 사용자가 입력한 전체 텍스트를 검색어로 사용
    else:
        # 추출된 첫 번째 지역을 검색할 지역으로 설정
        region = locations[0]
        # 추출된 키워드가 있으면 키워드를 검색어로 사용, 없으면 전체 텍스트 사용
        query = ' '.join(keywords) if keywords else search_input

    # 네이버 블로그와 구글의 맛집 데이터를 가져오는 크롤링 함수 호출
    naver_results = fetch_naver_blog_data(query=query, region=region, keywords=keywords)
    google_results = fetch_top_restaurants_nearby(query, region)

    # 네이버와 구글 결과를 합쳐서 저장
    combined_results = naver_results + google_results

    # 검색된 맛집 데이터를 기반으로 임베딩 벡터 생성
    embeddings = np.array([
        get_embedding(result.title + " " + result.description) for result in combined_results
    ], dtype='float32')

    # 임베딩이 비어 있을 경우 예외 처리
    if embeddings.size == 0:
        raise HTTPException(status_code=500, detail="임베딩이 생성되지 않았습니다.")

    # 벡터 차원 조정
    if embeddings.ndim == 3:
        embeddings = embeddings.reshape(-1, dimension)
    elif embeddings.ndim == 2:
        embeddings = embeddings
    elif embeddings.ndim == 1:
        embeddings = embeddings.reshape(1, dimension)

    # FAISS 인덱스에 벡터 저장
    store_vectors_in_faiss(embeddings)

    # 검색 결과를 템플릿에 전달하여 렌더링
    return templates.TemplateResponse("index.html", {
        "request": request,
        "search_results": combined_results  # 검색 결과 전달
    })
