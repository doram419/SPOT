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
    fetch('/search/', {
        method: 'POST',  // POST 메서드 명시
        body: formData  // FormData 전송
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text();  // 텍스트 응답을 받음
    })
    .then(html => {
        document.body.innerHTML = html;
    })
    .catch(error => {
        console.error('Error during fetch:', error);
        alert('Error: ' + error.message);
    });
}