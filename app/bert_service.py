import torch
from app.models_loader import tokenizer, bert_model


# BERT 임베딩 생성 함수
def get_embedding(text: str):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = bert_model(**inputs)
    # 마지막 레이어의 모든 토큰 평균을 임베딩으로 반환
    return outputs.last_hidden_state.mean(dim=1).numpy()



# 긴 문장을 청크로 나누는 함수
def chunk_text(text: str, chunk_size=512):
    tokens = tokenizer.tokenize(text)  # BERT 토크나이저로 토큰화
    # 512 토큰 단위로 청크로 나눔
    return [' '.join(tokens[i:i + chunk_size]) for i in range(0, len(tokens), chunk_size)]