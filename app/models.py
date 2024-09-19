from pydantic import BaseModel
from typing import Optional

class SearchResult(BaseModel):
    title: str
    link: str
    description: str
    rating: Optional[float] = None
    views: Optional[int] = None