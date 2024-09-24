import pymysql
from models import SearchResult
import pymysql

def create_connection():
    """
    MySQL 데이터베이스 연결을 생성하는 함수
    """
    return pymysql.connect(
        host='localhost',
        user='root',
        password='@tjgywjd77',
        database='spot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def saveToRDB(data: SearchResult):
    """
    MySQL DB에 데이터를 저장하고 생성된 PK를 반환하는 함수
    """
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            # 데이터 삽입 SQL 쿼리 추가할거있으면 추가하기 ************* title중복시 데이터 삽입XX 구현해야함*******
            sql = """
            INSERT INTO restaurant_search_results 
            (title, review, adr_address, international_phone_number)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data.title, data.review, data.adr_address, data.international_phone_number
            ))
            connection.commit()
            return cursor.lastrowid  # 삽입된 데이터의 기본 키(PK) 반환

    except Exception as e:
        print(f"데이터베이스 저장 중 오류 발생: {e}")
        return None

    finally:
        connection.close()
        print(cursor.lastrowid)


    """
    MySQL DB에 크롤링한 데이터를 저장하고 생성된 pk를 반환해주는 함수

    저장하는 데이터
    - 가게명, 리뷰, 주소, 국제 전화번호
    반환 값 
    - pk : int
    """

    # TODO:MySQL에 데이터 생성해서 넣기, 예외처리
    global temp_pk
    temp_pk += 1
    return temp_pk

def create_connection():
    """
    MySQL 데이터베이스 연결을 생성하는 함수
    """
    return pymysql.connect(
        host='localhost',
        user='root',
        password='manager#0912',
        database='spot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def saveToRDB(data: SearchResult):
    """
    MySQL DB에 데이터를 저장하고 생성된 PK를 반환하는 함수
    """
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            # 데이터 삽입 SQL 쿼리 추가할거있으면 추가하기 *************
            sql = """
            INSERT INTO restaurant_search_results 
            (title, review, adr_address, international_phone_number)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data.title, data.reviews[0]['text'], data.address, data.international_phone_number
            ))
            connection.commit()
            return cursor.lastrowid  # 삽입된 데이터의 기본 키(PK) 반환

    except Exception as e:
        print(f"데이터베이스 저장 중 오류 발생: {e}")
        return None

    finally:
        connection.close()

