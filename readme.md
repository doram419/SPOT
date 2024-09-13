## How to use 
내부적으로 naver API와 구글 API를 사용하고 있다
.env 파일로 해당 키를 관리하고 있고 해당 파일은 .gitignroe로 git에는 올라가지 않으니
하는 사람이 추가로 만들어서 할당해야 함

- 라이브러리 미설치시 아래 코드 터미널에 작성하기
-> requirements.txt 파일에 필요한 패키지 설치
pip install -r requirements.txt

- 실행시 터미널 입력
conda activate {가상환경이름}
uvicorn app.main:app --reload
======================================================================
# 주요 기능 설명: 
### fetch_google_places 함수:
Google Places API를 사용하여 지역을 위도/경도로 변환한 후, 리뷰가 많고 평점이 좋은 순서대로 상위 5개의 장소를 검색합니다.

### fetch_naver_blog_data 함수:
네이버 블로그 API를 사용하여 검색어와 지역에 맞는 블로그 게시글을 조회수 순으로 정렬하고 상위 5개의 결과를 반환합니다.

### extract_keywords 함수:
OpenAI GPT-3.5-turbo 모델을 사용하여 긴 문장을 청크로 나눈 후 각 청크에서 핵심 키워드를 추출하여 결합한 결과를 반환합니다.

### 검색 요청 처리:
/search/ 경로로 POST 요청이 들어오면, 키워드를 추출하여 네이버 블로그와 Google Places에서 각각 데이터를 가져와서 결합한 후, 결과를 템플릿에 전달하여 렌더링합니다.
이 코드는 검색된 결과를 HTML 템플릿을 통해 보여주고, 각 검색 결과는 title, description, link와 같은 필드로 구조화되어 있습니다.