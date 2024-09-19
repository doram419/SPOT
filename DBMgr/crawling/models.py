from pydantic import BaseModel
from typing import Optional

class SearchResult(BaseModel):
    title: str
    link: str
    description: str
    rating: Optional[float] = None
    views: Optional[int] = None
    # TODO: 주소 넣기
    # description은 큰 특징인데 rdb 저장이 사실상 불가능하지. Vector DB에 넣으면?
    # 다른 건 Vector DB에 넣을 필요성 있나?