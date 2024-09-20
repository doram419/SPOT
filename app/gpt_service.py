import openai
from app.config import OPENAI_API_KEY
from app.bert_service import chunk_text

# OpenAI API 키 설정
openai.api_key = OPENAI_API_KEY

# OpenAI GPT로 키워드 추출
def extract_keywords(text: str):
    chunks = chunk_text(text)
    keywords = []

    # 각 청크에 대해 GPT 모델을 사용하여 키워드 추출
    for chunk in chunks:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts keywords."},
                {"role": "user", "content": f"Extract keywords from the following text: {chunk}"}
            ]
        )
        keywords.append(response['choices'][0]['message']['content'].strip())

    return ' '.join(keywords)