from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def search_restaurants(location):
    # WebDriver 초기화 (Chrome 사용)
    driver = webdriver.Chrome()
    
    try:
        # 네이버 지도 접속
        driver.get("https://map.naver.com/")
        
        # 검색창 찾기 및 검색어 입력
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.input_search"))
        )
        search_box.send_keys(f"{location} 맛집")
        search_box.send_keys(Keys.ENTER)
        
        # 검색 결과 로딩 대기
        time.sleep(3)
        
        # iframe으로 전환
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#searchIframe"))
        )
        driver.switch_to.frame(iframe)
        
        # 음식점 리스트 가져오기
        restaurant_list = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.item_search"))
        )
        
        # 음식점 정보 추출
        for restaurant in restaurant_list[:5]:  # 상위 5개 음식점만 출력
            name = restaurant.find_element(By.CSS_SELECTOR, "span.search_title_text").text
            try:
                address = restaurant.find_element(By.CSS_SELECTOR, "span.address").text
            except:
                address = "주소 정보 없음"
            try:
                rating = restaurant.find_element(By.CSS_SELECTOR, "span.rating").text
            except:
                rating = "평점 정보 없음"
            
            print(f"이름: {name}")
            print(f"주소: {address}")
            print(f"평점: {rating}")
            print("-" * 50)
        
    finally:
        # WebDriver 종료
        driver.quit()

# 사용 예시
search_restaurants("서울 강남")