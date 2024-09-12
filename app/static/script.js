function search(event) {
    event.preventDefault();  // 페이지 새로고침 방지

    const searchTerm = document.getElementById('searchInput').value;
    const regionTerm = document.getElementById('regionInput').value;  // 지역 입력

    // 검색어와 지역이 비어있는지 확인
    if (!searchTerm || !regionTerm) {
        alert("검색어와 지역을 입력해주세요!");
        return;
    }

    // 서버로 검색 요청을 보냄 (POST 메서드 사용)
    fetch('http://127.0.0.1:8000/search/', {
        method: 'POST',  // POST 메서드 명시
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: searchTerm, region: regionTerm }),  // 검색어와 지역을 JSON으로 전송
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = "";  // 이전 결과를 지움

        // 검색 결과를 HTML로 추가
        data.search_results.forEach(result => {
            const resultItem = document.createElement('div');
            resultItem.innerHTML = `<h3>${result.title}</h3><p>${result.description}</p><a href="${result.link}" target="_blank">더보기</a>`;
            resultsDiv.appendChild(resultItem);
        });


    })
    .catch(error => {
        console.error('Error during fetch:', error);
        alert('Error: ' + error.message);
    });
}
