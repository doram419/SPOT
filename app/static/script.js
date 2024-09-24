// 검색 요청을 처리하는 함수
function search(event) {
    event.preventDefault();  // 페이지 새로고침 방지

    // 입력된 통합 검색어를 가져옴
    const searchInput = document.getElementById('searchInput').value;

    // 검색어가 입력되지 않았을 때 경고창 표시
    if (!searchInput) {
        alert("검색어와 지역을 입력하세요!");
        return;
    }

    // FormData 객체 생성
    const formData = new FormData();
    formData.append('search_input', searchInput);

    // 검색 요청을 서버에 전송
    fetch('http://127.0.0.1:8000/search/', {  // 서버의 URL 명확화
        method: 'POST',  // POST 메서드 명시
        body: formData  // FormData 전송
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok. Status: ' + response.status);
        }

        // 서버가 JSON을 반환하는 경우
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return response.json();
        }

        // 서버가 HTML을 반환하는 경우
        return response.text();
    })
    .then(data => {
        // JSON과 HTML 모두 처리 가능하도록 조건 분기
        if (typeof data === 'string') {
            document.body.innerHTML = data;  // HTML을 페이지에 적용
        } else {
            console.log('JSON 응답:', data);
            // 필요한 경우 JSON 데이터를 사용한 추가 로직
        }
    })
    .catch(error => {
        console.error('Error during fetch:', error);
        alert('Error: ' + error.message);
    });
}
