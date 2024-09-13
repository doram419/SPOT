from transformers import BertTokenizer, BertModel

# BERT 토크나이저 및 모델 로드
tokenizer = BertTokenizer.from_pretrained('klue/bert-base')
bert_model = BertModel.from_pretrained('klue/bert-base')
