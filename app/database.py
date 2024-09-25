from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# MySQL 연결 설정
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:0000@localhost/spot")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 데이터베이스 초기화
def init_db():
    Base.metadata.create_all(bind=engine)
