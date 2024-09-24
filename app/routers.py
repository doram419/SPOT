from fastapi import FastAPI, APIRouter, Request, Form, HTTPException # FastAPI에서 APIRouter, Request, Form 및 예외처리 기능을 가져옴
from fastapi.responses import HTMLResponse # HTML 응답을 처리하는 HTMLResponse를 가져옴
from fastapi.templating import Jinja2Templates # Jinja2 템플릿을 사용하여 HTML 파일을 렌더링하기 위해 가져옴
from app.crawling.google_service import fetch_top_restaurants_nearby # 구글 맛집 데이터 가져오는 함수
from app.crawling.naver_service import fetch_naver_blog_data # 네이버 블로그 데이터 가져오는 함수
from app.bert_service import get_embedding # 텍스트 임베딩을 생성하는 함수
import faiss # 벡터 검색 및 임베딩을 위한 라이브러리 FAISS
import numpy as np # Numpy는 벡터 및 배열 계산을 위한 라이브러리
import re  # 정규식을 사용하여 텍스트 패턴을 추출하는 라이브러리
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from transformers import pipeline, ElectraForTokenClassification, ElectraTokenizer  # KoELECTRA 모델을 위한 토크나이저 및 분류 모델 가져옴
from konlpy.tag import Okt  # KoNLPy의 Okt 형태소 분석기 가져오기

app = FastAPI()
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# 형태소 분석기 초기화
okt = Okt()

# 불용어 리스트 정의
stopwords = ['을', '를', '이', '가', '은', '는', '에', '에서', '으로', '로', '와', '과', '도',
             '하다', '있다', '되다', '이다', '의', '그리고', '또한', '하면서', '면서', '같다', '좋다']

# 미세 조정된 NER 모델 설정
try:
    tokenizer = ElectraTokenizer.from_pretrained("kykim/bert-kor-base")
    model = ElectraForTokenClassification.from_pretrained("kykim/bert-kor-base")
except Exception as e:
    logger.error(f"모델 로딩 중 오류 발생: {e}")
    raise HTTPException(status_code=500, detail="서버에서 오류가 발생했습니다.")

# NER 파이프라인 생성
ner_model = pipeline(
    "ner",
    model=model,
    tokenizer=tokenizer,
    aggregation_strategy="simple",
    #tokenizer_kwargs={"clean_up_tokenization_spaces": True}
) # NER 태스크를 위한 파이프라인 생성

# 엔티티 매핑 테이블
entity_mapping = {
    'LOC': 'location',
    'ORGANIZATION': 'organization',
    'PERSON': 'person',
    'O': 'others'
}

# FAISS 인덱스 초기화
embedding_dimension = 768
# index = faiss.IndexFlatL2(embedding_dimension)

# 한국 주요 지역 리스트
korean_locations = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]


# 지역명 추출 함수 (정규식 사용)
def extract_location_with_regex(text: str):
    loc_patterns = re.findall(r'\w+역|\w+동', text)
    for location in korean_locations:
        if location in text:
            loc_patterns.append(location)
    return loc_patterns

# 형태소 분석을 통한 키워드 추출 함수
def extract_keywords_with_morph(text):
    tokens = okt.pos(text, stem=True)
    keywords = [word for word, pos in tokens if pos in ['Noun', 'Verb', 'Adjective']]
    keywords = [word for word in keywords if word not in stopwords]
    return keywords

# NER과 정규식을 사용한 지역 및 키워드 추출
def extract_entities_and_keywords(text: str):
    entities = ner_model(text)
    locations = extract_location_with_regex(text)
    keywords = []

    # NER 결과 처리
    for entity in entities:
        word = entity.get('word', entity.get('text', '')).replace('##', '')
        entity_label = entity.get('entity_group', entity.get('entity', ''))

        # 엔티티 레이블 매핑
        category = entity_mapping.get(entity_label, 'keyword')

        if category == 'location':
            locations.append(word)
        else:
            keywords.append(word)

    # 형태소 분석을 통한 추가 키워드 추출
    morph_keywords = extract_keywords_with_morph(text)
    keywords.extend(morph_keywords)

    # 불용어 제거 및 중복 제거
    keywords = list(set(keywords))
    locations = list(set(locations))

    return locations, keywords


# 벡터 저장 함수
# store_vectors_in_faiss(vectors: np.ndarray):
 #   if len(vectors.shape) > 2:
  #      vectors = np.squeeze(vectors)
   # if len(vectors.shape) != 2 or vectors.shape[1] != embedding_dimension:
    #    raise ValueError(f"Expected 2D array with shape [{None}, {embedding_dimension}], but got {vectors.shape}")
    #index.add(vectors)

# 검색 처리 엔드포인트
@router.post("/search/", response_class=HTMLResponse)
async def search_restaurant(request: Request, search_input: str = Form(...)):
    if not search_input:
        raise HTTPException(status_code=400, detail="검색어를 입력하세요.")

    logger.info(f"입력된 검색어: {search_input}")  # 검색어 로그 출력

    # 지역 및 키워드 추출
    locations, keywords = extract_entities_and_keywords(search_input)
    logger.info(f"추출된 지역: {locations}, 추출된 키워드: {keywords}")  # 추출된 NER 결과 로그 출력

    if not locations:
        region = "서울"
    else:
        region = locations[0]

    query = ' '.join(keywords) if keywords else search_input
    print(f"최종 검색어: {query}, 지역: {region}")  # 최종 검색 쿼리와 지역 확인

    # 네이버 및 구글 검색 결과
    try:
        naver_results = fetch_naver_blog_data(query, region, keywords)
        logger.info(f"네이버 결과 가져오기 완료")
    except Exception as e:
        logger.error(f"네이버 블로그 데이터 가져오는 중 오류 발생: {e}")
        naver_results = []

    try:
        google_results = fetch_top_restaurants_nearby(query, region)
        logger.info(f"구글 결과 가져오기 완료")
    except Exception as e:
        logger.error(f"구글 맛집 데이터 가져오는 중 오류 발생: {e}")
        google_results = []

    logger.info(f"네이버 검색 결과: {len(naver_results)}개, 구글 검색 결과: {len(google_results)}개")  # 데이터 가져온 후 로그 출력

    combined_results = naver_results + google_results

    if not combined_results:
        logger.error("검색 결과가 없습니다.")
        raise HTTPException(status_code=404, detail="검색 결과가 없습니다.")

    # 요청 내에서 FAISS 인덱스 초기화
    index = faiss.IndexFlatL2(embedding_dimension)

    # 임베딩 생성 및 인덱스에 추가
    try:
        embeddings = np.array([get_embedding(result.title + " " + result.description) for result in combined_results],
                              dtype='float32')
        logger.info(f"임베딩 생성 완료, shape: {embeddings.shape}")
        if embeddings.size == 0:
            logger.error("임베딩 생성 결과가 없습니다.")
            raise HTTPException(status_code=500, detail="임베딩 생성 결과가 없습니다.")
    except Exception as e:
        logger.error(f"임베딩 생성 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="임베딩 생성 중 오류가 발생했습니다.")

    if embeddings.ndim == 3:
        embeddings = embeddings.reshape(-1, embeddings.shape[-1])

    index.add(embeddings)
    logger.info(f"FAISS 인덱스에 벡터 추가 완료, 총 벡터 수: {index.ntotal}")

    # 검색어 임베딩 생성 및 FAISS 검색
    try:
        query_embedding = np.array([get_embedding(query)], dtype='float32')
        if query_embedding.size == 0:
            logger.error("검색어 임베딩 생성 결과가 없습니다.")
            raise HTTPException(status_code=500, detail="검색어 임베딩 생성 결과가 없습니다.")
    except Exception as e:
        logger.error(f"검색어 임베딩 생성 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="검색어 임베딩 생성 중 오류가 발생했습니다.")

    logger.info(f"query_embedding shape: {query_embedding.shape}")

    # 차원 조정
    if len(query_embedding.shape) > 2:
        query_embedding = query_embedding.reshape(-1, query_embedding.shape[-1])
    elif len(query_embedding.shape) == 1:
        query_embedding = query_embedding.reshape(1, -1)

    try:
        distances, indices = index.search(query_embedding, k=5)
        logger.info(f"FAISS 검색 완료, distances: {distances}, indices: {indices}")
    except Exception as e:
        logger.error(f"FAISS 검색 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="검색 중 오류가 발생했습니다.")

    # 검색 결과 추출
    search_results = [combined_results[idx] for idx in indices[0]]
    logger.info(f"검색된 결과: {search_results}")  # FAISS 검색 결과 로그 출력

    return templates.TemplateResponse("index.html", {"request": request, "search_results": search_results, "naver_results": naver_results, "google_results": google_results})

# 메인 페이지 엔드포인트
@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# FastAPI 라우터 등록
app.include_router(router)
