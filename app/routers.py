from fastapi import FastAPI, APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.crawling.google_service import fetch_top_restaurants_nearby
from app.crawling.naver_service import fetch_naver_blog_data
from app.bert_service import get_embedding
import faiss
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import re
import logging

app = FastAPI()
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# KoELECTRA NER 모델 설정
tokenizer = AutoTokenizer.from_pretrained("monologg/koelectra-base-v3-discriminator")
model = AutoModelForTokenClassification.from_pretrained("monologg/koelectra-base-v3-discriminator")
ner_model = pipeline("ner", model=model, tokenizer=tokenizer)

# FAISS 인덱스 초기화
dimension = 768
index = faiss.IndexFlatL2(dimension)

# 한국 주요 지역 리스트
korean_locations = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]


# 지역명 추출 함수 (정규식 사용)
def extract_location_with_regex(text: str):
    loc_patterns = re.findall(r'\w+역|\w+동', text)
    for location in korean_locations:
        if location in text:
            loc_patterns.append(location)
    return loc_patterns


# NER과 정규식을 사용한 지역 및 키워드 추출
def extract_entities(text: str):
    entities = ner_model(text)
    locations, keywords = [], []

    # 정규식으로 지역명 추출
    regex_locations = extract_location_with_regex(text)
    locations.extend(regex_locations)

    # NER 결과 처리
    for entity in entities:
        word = entity['word'].replace('##', '')
        if entity['entity'] == 'LOC':
            locations.append(word)
        else:
            keywords.append(word)

    return locations, keywords


# 벡터 저장 함수
def store_vectors_in_faiss(vectors: np.ndarray):
    if len(vectors.shape) > 2:
        vectors = np.squeeze(vectors)
    if len(vectors.shape) != 2 or vectors.shape[1] != dimension:
        raise ValueError(f"Expected 2D array with shape [{None}, {dimension}], but got {vectors.shape}")
    index.add(vectors)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 검색 처리 엔드포인트
@router.post("/search/", response_class=HTMLResponse)
async def search_restaurant(request: Request, search_input: str = Form(...)):
    if not search_input:
        raise HTTPException(status_code=400, detail="검색어를 입력하세요.")

    logger.info(f"입력된 검색어: {search_input}")  # 검색어 로그 출력

    # 지역 및 키워드 추출
    locations, keywords = extract_entities(search_input)
    logger.info(f"추출된 지역: {locations}, 추출된 키워드: {keywords}")  # 추출된 NER 결과 로그 출력

    if not locations:
        region = "서울"
    else:
        region = locations[0]

    query = ' '.join(keywords) if keywords else search_input
    print(f"최종 검색어: {query}, 지역: {region}")  # 최종 검색 쿼리와 지역 확인

    # 네이버 및 구글 검색 결과
    naver_results = fetch_naver_blog_data(query, region, keywords)
    google_results = fetch_top_restaurants_nearby(query, region)

    logger.info(f"네이버 검색 결과: {len(naver_results)}개, 구글 검색 결과: {len(google_results)}개")  # 데이터 가져온 후 로그 출력

    combined_results = naver_results + google_results

    # 임베딩 생성
    embeddings = np.array([get_embedding(result.title + " " + result.description) for result in combined_results],
                          dtype='float32')

    if embeddings.ndim == 3:
        embeddings = embeddings.reshape(-1, dimension)

    store_vectors_in_faiss(embeddings)

    # 검색어 임베딩 생성 및 FAISS 검색
    query_embedding = np.array([get_embedding(query)], dtype='float32')
    distances, indices = index.search(query_embedding, k=5)

    # 검색 결과 추출
    search_results = [combined_results[idx] for idx in indices[0]]
    logger.info(f"검색된 결과: {search_results}")  # FAISS 검색 결과 로그 출력

    return templates.TemplateResponse("index.html", {"request": request, "search_results": search_results})


# 메인 페이지 엔드포인트
@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# FastAPI 라우터 등록
app.include_router(router)
