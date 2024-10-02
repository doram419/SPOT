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
                {"role": "system", "content": (
                    "당신은 한국의 맛집 전문가입니다. "
                    "사용자가 제공한 가게 정보를 바탕으로 핵심적인 요약을 제공하는 것이 목표입니다. "
                    "요약은 사용자가 가게를 빠르게 이해할 수 있도록 간결하고 명확해야 합니다."
                )},
                {"role": "user", "content": f"""
                가게 이름: {name}\n
                가게 설명: {desc}\n
                아래 항목을 기준으로 요약을 작성하세요:\n
                대표 메뉴: 가게의 인기 메뉴를 강조하세요.\n
                위치: 가게의 위치를 짧게 요약하세요 (동네, 도시).\n
                분위기: 가게의 분위기를 간결하게 설명하세요 (예: 로맨틱한, 캐주얼한, 가족 친화적인 등).\n
                차별점: 이 가게만의 특별한 특징을 강조하세요.\n
                최대 200자로 요약을 간결하게 작성하세요.
                """}
            ],
            temperature=0.7,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0.5,  # 중복된 내용에 대한 패널티
            presence_penalty=0.5    # 새로운 정보에 대한 장려
        )
        result = response.choices[0].message.content
        print("요약결과"+result)
        # print("desc"+desc)
        return result

    except Exception as e:
        print(f"OpenAI API 오류 발생: {e}")
        return "요약 생성 실패"