# 필요한 라이브러리 임포트
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.crawling.google_service import fetch_top_restaurants_nearby
from app.crawling.naver_service import fetch_naver_blog_data
from app.bert_service import get_embedding
import faiss
import numpy as np
import re

from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

tokenizer = AutoTokenizer.from_pretrained("kykim/bert-kor-base")
model = AutoModelForTokenClassification.from_pretrained("kykim/bert-kor-base")

ner_model = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

# 임의의 임베딩 벡터 생성
dimension = 768
vectors = np.random.rand(100, dimension).astype('float32')

# faiss 인덱스 생성 및 벡터 추가
index = faiss.IndexFlatL2(dimension)
index.add(vectors)

# 벡터 저장 함수
def store_vectors_in_faiss(vectors: np.ndarray):
    if vectors.size == 0:
        raise ValueError("벡터 배열이 비어 있습니다. 벡터를 추가할 수 없습니다.")

    # 벡터 차원 조정
    if len(vectors.shape) > 2:
        vectors = np.squeeze(vectors)
    if len(vectors.shape) != 2 or vectors.shape[1] != dimension:
        raise ValueError(f"벡터의 차원이 올바르지 않습니다. 예상: 2D 배열 [{None}, {dimension}], 받은: {vectors.shape}")

    index.add(vectors)  # FAISS 인덱스에 벡터 추가

# 한국 주요 지역명 리스트 (필요시 확장 가능)
korean_locations = [
    "서울", "부산", "대구", "인천", "광주", "대전", "울산",
    "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
    "속초", "춘천", "양양", "횡성", "양평","전주","남양주","강릉"
]

# 정규식을 사용한 지역 추출 함수
def extract_location_with_regex(text: str):
    loc_patterns = re.findall(r'\w+역|\w+동|\w+시|\w+구|\w+군', text)

    # 사전 정의된 지역명과 일치하는지 확인
    for location in korean_locations:
        if location in text:
            loc_patterns.append(location)

    return loc_patterns

# NER과 정규식을 병행하여 지역과 키워드 추출
def extract_entities(text: str):
    # NER 추출
    entities = ner_model(text)
    print(f"NER 결과: {entities}")

    locations = []
    keywords = []

    # 정규식을 사용한 지역명 추출
    regex_locations = extract_location_with_regex(text)
    locations.extend(regex_locations)

    # NER 결과에서 단어 추출
    for entity in entities:
        word = entity['word']
        entity_label = entity.get('entity_group', '')  # 'entity_group'이 없는 경우 기본값 제공

        # 예상 레이블이 아닌 경우에도 키워드로 처리
        if 'LOC' in entity_label or 'GPE' in entity_label:
            locations.append(word)
        else:
            keywords.append(word)

    # 만약 NER에서 지역을 추출하지 못했으면 정규식 결과를 우선 사용
    if not locations and regex_locations:
        locations = regex_locations

    # 중복 제거
    locations = list(set(locations))
    keywords = list(set(keywords))

    return locations, keywords

# FastAPI의 APIRouter 인스턴스 생성
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# GET 요청 처리, 메인 페이지 렌더링
@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# POST 요청을 통해 검색을 처리하는 엔드포인트
@router.post("/search/", response_class=HTMLResponse)
async def search_restaurant(request: Request, search_input: str = Form(...)):
    if not search_input:
        raise HTTPException(status_code=400, detail="검색어를 입력하세요.")

    print(f"검색어: {search_input}")

    # NER 및 정규식을 사용하여 지역(LOC) 및 키워드 추출
    locations, keywords = extract_entities(search_input)
    print(f"추출된 지역: {locations}, 추출된 키워드: {keywords}")

    if not locations:
        region = "서울"  # 기본 지역 설정
        query = search_input
    else:
        region = locations[0]  # 첫 번째 지역 선택
        query = ' '.join(keywords) if keywords else search_input

    # 네이버 블로그 및 구글 맛집 데이터 가져오기
    naver_results = fetch_naver_blog_data(query=query, region=region, keywords=keywords)
    google_results = fetch_top_restaurants_nearby(query, region)

    combined_results = naver_results + google_results  # 결과 합치기

    # 임베딩 벡터 생성
    embeddings = np.array([
        get_embedding(result.title + " " + result.description) for result in combined_results
    ], dtype='float32')

    if embeddings.size == 0:
        raise HTTPException(status_code=500, detail="임베딩이 생성되지 않았습니다.")

    # 벡터 차원 조정
    if embeddings.ndim == 3:
        embeddings = embeddings.reshape(-1, dimension)
    elif embeddings.ndim == 2:
        embeddings = embeddings
    elif embeddings.ndim == 1:
        embeddings = embeddings.reshape(1, dimension)

    store_vectors_in_faiss(embeddings)  # FAISS 인덱스에 벡터 저장

    # 검색 결과 렌더링
    return templates.TemplateResponse("index.html", {
        "request": request,
        "search_results": combined_results  # 템플릿에 검색 결과 전달
    })
