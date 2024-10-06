

def make_naver_data(url : str): 
    # url로 request를 보내서 response를 받아온다
    response = requests.get(url)
    # python의 내부 html.parser로 html 전문을 파싱해서 가져온다.
    soup = BeautifulSoup(response.text, 'html.parser')

    # <iframe></iframe>식의 태그를 문서 내부에서 찾는다.
    # 여러 개를 가져오는지 제일 처음 하나를 가져오는지는 잘 모르겠다
    iframe_tag = soup.find('iframe')
    # iframe은 html안에 다른 html을 요청하는 것. 그래서 그 html의 주소는 src.
    # src 속성 추출
    # 추출된 속성은 온전한 html이 아닐수도 있다
    # 추출이 실패할 수도 있다
    iframe_src = iframe_tag['src']

    naver_blog_url = 'https://blog.naver.com/'

    # iframe이 가리키는 URL에 대해 별도로 요청
    if iframe_src != None:
        iframe_response_url = naver_blog_url + iframe_src
        iframe_response = requests.get(iframe_response_url)
        iframe_soup = BeautifulSoup(iframe_response.text, 'html.parser')
        
        # class="se-main-container"를 가진 <div> 태그 찾기
        div_container = iframe_soup.find('div', class_='se-main-container')
        refined_content = div_container.text.replace('\n', ' ')
        
        # 네이버 블로그에 내장된 지도에서 이름 가져오기
        title = iframe_soup.find('strong', class_='se-map-title')
        refined_title = title.text
        
        # 네이버 블로그에 내장된 지도에서 주소 가져오기
        address = iframe_soup.find('p', class_='se-map-address')
        refined_address = address.text

        # 네이버 지도가 없는 경우도 생각해야 함
        print(refined_title)
        print(refined_address)
        # print(refined_content)



    
    
