## <img src="logo.PNG" alt="Spot Logo" width="50" /> 사용자 맞춤형 맛집 추천 웹 서비스 Spot
안녕하세요. "Spot"은 LLM(OpenAI)과 LangChain을 활용하여 사용자의 검색 문장을 자연어로 분석하고, 의도를 파악해 최적의 맛집을 추천하는 사용자 맞춤형 맛집 추천 웹 서비스입니다. 단순 키워드 검색이 아닌 의미 기반 검색을 통해 더욱 정교하고 개인화된 추천을 제공합니다.

## 구동모습  
<img src="readme source/search.gif" alt="사용자가 예시 카드에 있는 카드를 눌러서 검색해주는 모습이 보여지고 있음" width="800"/>
* 사용자가 예시 카드에 있는 "친구들과 청첩장 모임하기 좋은 레스토랑 찾아줘"라는 카드를 눌러서 검색해주는 모습입니다.
<br/>
<br/>
<br/>
    
<img src="readme source/result.jpg" alt="검색된 결과가 보이는 이미지" width="800"/>   
* 결과 사진의 모습. 추천이유와 차별점에 대해서 기술되어 있습니다.
<br/>
   
<img src="readme source/result.gif" alt="여러 개의 결과가 사용자의 입력에 맞춰 넘어가며 보인다" width="800"/>
* 최적의 하나 말고 여러 결과를 찾아주어서 원하는 걸 볼 수 있게 했습니다.
<br/>
    
## <img src="readme source/python.png" alt="파이썬 이미지" width="50" /> 개발 스택

사용자 서비스용 : <b> Spot </b>
- 프론트 : JavaScript, CSS
- 백엔드 : Python
- 프레임워크 : FastAPI
- 기타: OpenAI, NaverAPI, Google Map, Faiss Vector DB
형상 관리 도구 : Git

데이터 수집 지원 툴 : <b>Good DB Mgr</b>
- Python, tkinker, Faiss Vector DB
