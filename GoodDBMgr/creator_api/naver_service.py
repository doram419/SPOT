import re
import requests
from urllib import parse
from bs4 import BeautifulSoup
from .datas.naver_data import NaverData
from .api_key import get_key
from .ocr_service import perform_ocr_from_url

class NaverService():
    def __init__(self) -> None:
        self.naver_key = get_key("NAVER_CLIENT_ID")
        self.naver_secret = get_key("NAVER_CLIENT_SECRET")

    def crawling_naver_blog_data(self,
            query: str = "검색할 가게명", region :str = "검색할 지명", 
            display: int = 10) :
        """
        네이버 블로그 데이터 최대한 많이 (최대100개) 가져오기
        display : 한 구글 지역에 매칭될 수량 10~100
        """
        try:
            # 지역과 검색어를 결합하여 검색
            combined_query = f"{region} {query}"
            enc_text = parse.quote(combined_query)
            base_url = "https://openapi.naver.com/v1/search/blog.json"

            headers = {
                "X-Naver-Client-Id": self.naver_key,
                "X-Naver-Client-Secret": self.naver_secret
            }

            start = 1
            sort = "sim"

            url = f"{base_url}?query={enc_text}&display={display}&start={start}&sort={sort}"

            # 네이버 블로그 API 호출
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            items = response.json().get("items", [])
            blogs = list()
            for item in items:
                link = item.get('link')
                blogs.append(self.make_naver_data(blog_url=link))
            
            return blogs

        except requests.exceptions.RequestException as e:
            print(f"Naver API 요청 실패: {str(e)}")
            return "네이버 블로그 설명 오류"
        
    def make_naver_data(self, blog_url : str) -> NaverData: 
        """
        추출이 안되면 None 반환
        """
        # url로 request를 보내서 response를 받아온다
        response = requests.get(blog_url)
        # python의 내부 html.parser로 html 전문을 파싱해서 가져온다.
        soup = BeautifulSoup(response.text, 'html.parser')

        # <iframe></iframe>식의 태그를 문서 내부에서 찾는다.
        # 여러 개를 가져오는지 제일 처음 하나를 가져오는지는 잘 모르겠다
        iframe_tag = soup.find('iframe')
        # iframe은 html안에 다른 html을 요청하는 것. 그래서 그 html의 주소는 src.
        # src 속성 추출
        iframe_src = iframe_tag['src'] if iframe_tag else None

        naver_blog_url = 'https://blog.naver.com/'

        # iframe이 가리키는 URL에 대해 별도로 요청
        if iframe_src != None:
            iframe_response_url = naver_blog_url + iframe_src
            headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            iframe_response = requests.get(iframe_response_url, headers=headers)
            iframe_soup = BeautifulSoup(iframe_response.text, 'html.parser')
            
            # class="se-main-container"를 가진 <div> 태그 찾기
            div_container = iframe_soup.find('div', class_='se-main-container')
            refined_content = str()
            if div_container:
                refined_content = div_container.text.replace('\n', ' ')

                # 이미지 태그 찾기
                img_tags = div_container.find_all('img', class_ ='se-image-resource')
                ocr_results = []
                for img_tag in img_tags:
                    # data-lazy-src가 고화질을 가르키고 있음 우선적으로 사용 없으면 src 사용
                    img_url = img_tag.get('data-lazy-src') or img_tag.get('src')
                    if 'type=' in img_url:
                         img_url = re.sub(r'type=[^&]*', 'type=w773', img_url)
                    else:
                        img_url = img_url

                    print(f"최종 이미지 URL: {img_url}")

                    # User-Agent 헤더를 포함하여 이미지 요청
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                        "Referer": blog_url  # Referer 추가
                    }
                    response = requests.get(img_url, headers=headers)

                    if response.status_code == 200:
                        print(f"이미지 크기: {len(response.content)} bytes")

                         # 이미지 URL을 이용해서 OCR 수행하기
                        ocr_text = perform_ocr_from_url(img_url)
                        if ocr_text:
                            ocr_results.append(f"[OCR 결과 시작] {ocr_text} [OCR 결과 끝]")
                            # OCR 결과를 출력하여 확인
                            print(f"OCR 결과: {ocr_text}")

                    else:
                        print(f"이미지 다운로드 실패: {response.status_code}")

                # OCR 결과를 추가하기
                if ocr_results:
                    refined_content += " " + " ".join(ocr_results)
            
            # 네이버 블로그에 내장된 지도에서 이름 가져오기
            title = iframe_soup.find('strong', class_='se-map-title')
            refined_title = str()
            if title:
                refined_title = title.text
            
            # 네이버 블로그에 내장된 지도에서 주소 가져오기
            address = iframe_soup.find('p', class_='se-map-address')
            refined_address = str()
            if address:
                refined_address = address.text

            return NaverData(title=refined_title, address=refined_address, content=refined_content, link=blog_url)
        
        return None
    
     # 여기에서 테스트용 블로그 URL로 데이터를 추출하는 함수를 추가
    def test_make_naver_data(self, blog_url: str):
        """
        특정 블로그 URL로부터 데이터를 추출하는 테스트 함수
        """
        naver_data = self.make_naver_data(blog_url=blog_url)
        if naver_data:
            print("블로그 제목:", naver_data.title)
            print("블로그 주소:", naver_data.address)
            print("블로그 내용:", naver_data.content)
            print("=" * 40)
        else:
            print("데이터 추출 실패")
            
if __name__ == "__main__":
    naver_service = NaverService()
    test_url = "https://blog.naver.com/95yulee/223288290394"
    naver_service.test_make_naver_data(blog_url=test_url)




    
    