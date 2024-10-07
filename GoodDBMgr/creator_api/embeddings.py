from .datas.constants import EMBEDDING_MODEL_TYPES, EMBEDDING_MODEL_VERSIONS
from langchain_openai import OpenAIEmbeddings 
import json
from .api_key import get_key
import numpy as np

class EmbeddingModule():
    def __init__(self, model_name, version) -> None:
        self.model_name = model_name
        self.version = version
        self.instance = None

    def get_embedding_instance(self):
        """
        외부 호출 x
        """
        if (self.model_name in EMBEDDING_MODEL_TYPES) and (self.version in EMBEDDING_MODEL_VERSIONS[self.model_name]):
            if self.model_name == "OpenAI":
                self.instance = OpenAIEmbeddings(openai_api_key=get_key("OPENAI_API_KEY"), model=self.version)
        
    def get_text_embedding(self, text): 
        """
        자연어 임베딩을 생성하는 함수
        :param text: 임베딩 할 텍스트
        :return: 임베딩 벡터
        """
        if self.instance == None:
            self.get_embedding_instance()

        if isinstance(text, dict):
            text = json.dumps(text, ensure_ascii=False)
        elif not isinstance(text, str):
            text = str(text)

        embedded_result = self.instance.embed_query(text)
        
        return np.array(embedded_result, dtype=np.float32)
            