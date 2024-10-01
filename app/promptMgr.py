from dotenv import load_dotenv
from app.config import OPENAI_API_KEY
from langchain.schema import Document  
from openai import OpenAI

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)

# 프롬프트
def summarize_desc(name: str, desc):
    """
    가게 이름과 설명을 바탕으로 OpenAI를 통해 요약된 정보를 반환하는 함수.
    중복된 정보 없이 새로운 정보를 생성하는 것을 목표로 함.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 맛집 전문가입니다. 사용자가 입력한 검색어에 대한 유익한 요약을 제공하는 것이 목표입니다."},
                {"role": "user", "content": f"""가게 이름: {name}\n
                가게 설명: {desc}\n
                1. 가게의 인기 메뉴(대표 메뉴)를 우선적으로 포함하세요.
                2. 가게의 위치(도시나 동네)를 짧게 요약하세요.
                3. 가게의 분위기(로맨틱한, 가족 친화적인, 캐주얼한 등)를 간결하게 설명하세요.
                4. 해당 가게와 관련된 중복된 정보는 제공하지 말고 새로운 내용을 만들어 주세요.
                5. 요약은 200자 이내로 하세요.
                6. 요약할 수 없는 정보는 생략하세요."""}

            ],
            temperature=0.7,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0.5,  # 중복된 내용에 대한 패널티
            presence_penalty=0.5    # 새로운 정보에 대한 장려
        )
        result = response.choices[0].message.content
        print("요약결과"+result)
        print("desc"+desc)
        return result

    except Exception as e:
        print(f"OpenAI API 오류 발생: {e}")
        return "요약 생성 실패"