from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)


class SearchResult(BaseModel):
    title: str
    link: str
    description: str
    rating: Optional[float] = None
    views: Optional[int] = None