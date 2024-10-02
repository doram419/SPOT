"""
사용자 정의 에러를 정의함!
"""
class VectorSearchException(Exception):
    """Vector 검색 관련 기본 예외"""
    pass

class EmptySearchQueryException(VectorSearchException):
    """검색어가 비어있을 때 발생하는 예외"""
    def __init__(self, message="검색어를 입력하세요."):
        self.message = message
        super().__init__(self.message)

class NoSearchResultsException(VectorSearchException):
    """검색 결과가 없을 때 발생하는 예외"""
    def __init__(self, message="검색 결과가 없습니다."):
        self.message = message
        super().__init__(self.message)

class EmptyVectorStoreException(VectorSearchException):
    """벡터 저장소가 비어있을 때 발생하는 예외"""
    def __init__(self, message="벡터 저장소에 데이터가 없습니다."):
        self.message = message
        super().__init__(self.message)