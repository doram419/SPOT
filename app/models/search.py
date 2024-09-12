import numpy as np
from fastapi import HTTPException
from transformers import BertTokenizer, BertModel, GPT2LMHeadModel, GPT2Tokenizer
import torch

# BERT와 GPT-2 모델 및 해당 토크나이저(tokenizer) 로드
# - `BertTokenizer`: BERT 모델을 위한 입력을 토큰화하는 데 사용됩니다.
# - `BertModel`: 미리 학습된 KLUE-BERT 모델로, 문장의 임베딩(벡터화)을 담당합니다.
# - `GPT2Tokenizer`: GPT-2 모델을 위한 입력을 토큰화하는 데 사용됩니다.
# - `GPT2LMHeadModel`: GPT-2 모델로, 검색된 결과를 바탕으로 답변을 생성합니다.

tokenizer = BertTokenizer.from_pretrained('klue/bert-base')  # KLUE-BERT 토크나이저 로드
bert_model = BertModel.from_pretrained('klue/bert-base')  # KLUE-BERT 모델 로드
gpt_tokenizer = GPT2Tokenizer.from_pretrained('gpt2')  # GPT-2 토크나이저 로드
gpt_model = GPT2LMHeadModel.from_pretrained('gpt2')  # GPT-2 모델 로드


def vector_search(query: str, data: list):
    """BERT 기반 벡터 검색을 수행하는 함수"""
    try:
        # 입력 쿼리를 임베딩(벡터화)하여 BERT 기반으로 변환
        query_embedding = get_embedding(query)
        results = []

        # 주어진 데이터에서 각 결과의 설명을 임베딩하고 유사도 계산
        for result in data:
            description_embedding = get_embedding(result.description)
            similarity = cosine_similarity(query_embedding, description_embedding)
            results.append((similarity, result))

        # 유사도 기준으로 결과 정렬 (내림차순)
        results = sorted(results, key=lambda x: x[0], reverse=True)

        # 유사도가 0.5 이상인 결과만 반환
        return [res for sim, res in results if sim > 0.5]

    except Exception as e:
        # 예외 발생 시 로그를 남기고 HTTP 500 에러 반환
        print(f"Vector search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Vector search failed")


def get_embedding(text: str):
    """KLUE-BERT로 텍스트를 벡터화"""
    # 텍스트를 토크나이저로 토큰화하고 BERT 모델 입력에 맞게 변환
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    # BERT 모델을 사용해 텍스트의 임베딩(벡터)을 추출
    with torch.no_grad():
        outputs = bert_model(**inputs)

    # BERT의 마지막 히든 스테이트의 평균값을 반환하여 텍스트 임베딩으로 사용
    return outputs.last_hidden_state.mean(dim=1).numpy()


def cosine_similarity(vec1, vec2):
    """두 벡터 간의 코사인 유사도를 계산하는 함수"""
    # 벡터를 numpy 배열로 변환하고 평탄화 (1차원 배열로 변환)
    vec1 = np.array(vec1).flatten()
    vec2 = np.array(vec2).flatten()

    # 벡터 간의 내적(dot product)을 계산
    dot_product = np.dot(vec1, vec2)

    # 각 벡터의 크기(노름, norm)를 계산
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)

    # 코사인 유사도 계산: 두 벡터의 내적을 각 벡터의 크기의 곱으로 나눔
    return dot_product / (norm_vec1 * norm_vec2)


def generate_rag_response(query: str, results: list):
    """GPT-2 모델을 사용하여 검색 결과를 요약하는 함수"""
    # 검색 결과의 제목과 설명을 하나의 문자열로 결합하여 문맥을 형성
    context = "\n".join([f"Title: {res.title}, Description: {res.description}" for res in results])

    # 사용자 쿼리와 검색 결과를 기반으로 답변을 생성하기 위한 GPT-2 프롬프트(prompt) 생성
    prompt = f"사용자가 '{query}'에 대해 물어봤습니다. 검색 결과:\n{context}\n\n이 정보를 참고하여 답변을 생성해 주세요:"

    # 프롬프트를 GPT-2 입력으로 인코딩
    inputs = gpt_tokenizer.encode(prompt, return_tensors="pt")

    # GPT-2 모델을 사용하여 답변 생성
    outputs = gpt_model.generate(inputs, max_length=150, num_return_sequences=1)

    # 생성된 답변을 디코딩하여 사람이 읽을 수 있는 텍스트로 변환
    generated_text = gpt_tokenizer.decode(outputs[0], skip_special_tokens=True)

    return generated_text
