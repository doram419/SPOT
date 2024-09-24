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
                {"role": "system",
                 "content": "You are an assistant that extracts restaurant search keywords and helps with sentence-based searches, prioritizing location and cuisine."},
                {"role": "user",
                 "content": f"From the following text, extract keywords focusing on two main priorities: 1) the location (such as city, district, or neighborhood) and 2) the type of cuisine (such as food or restaurant type). The goal is to find relevant restaurants in the specified area and for the specified type of food: {chunk}"}
            ]
        )
        keywords.append(response['choices'][0]['message']['content'].strip())

    return ' '.join(keywords)