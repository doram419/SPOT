from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, String, Integer, Boolean, Float
from sqlalchemy.orm import Session

class SearchResult(BaseModel):  # 주석처리돼있는거는 나중에 추가
    title: str
    link: str
    description: str
    adr_address: Optional[str] = None
    rating: Optional[float] = None
    views: Optional[int] = None
    price_level: Optional[int] = None
    serves_beer: Optional[bool] = None
    serves_wine: Optional[bool] = None
    serves_breakfast: Optional[bool] = None
    serves_brunch: Optional[bool] = None
    serves_lunch: Optional[bool] = None
    serves_dinner: Optional[bool] = None
    serves_vegetarian_food: Optional[bool] = None
    takeout: Optional[bool] = None
    status: Optional[bool] = None


    # TODO: 주소 넣기
    # description은 큰 특징인데 rdb 저장이 사실상 불가능하지. Vector DB에 넣으면?
    # 다른 건 Vector DB에 넣을 필요성 있나?
    # 별점데이터는 rdb에 적재