from sqlalchemy import create_engine # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
import os

# MySQL 연결 설정
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:himedia@localhost/spot")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 데이터베이스 초기화
def init_db():
    Base.metadata.create_all(bind=engine)
