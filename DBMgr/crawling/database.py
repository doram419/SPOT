from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL 데이터베이스 연결 설정
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://username:password@localhost/db_name"

# 엔진 생성
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 세션 로컬 객체 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 베이스 클래스 생성
Base = declarative_base()

# 데이터베이스 테이블 생성 함수
def init_db():
    Base.metadata.create_all(bind=engine)
