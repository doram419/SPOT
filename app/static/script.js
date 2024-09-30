document.addEventListener("DOMContentLoaded", function() {
    // DOM 요소 가져오기
    const voiceSearchButton = document.getElementById('voiceSearchButton');
    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');
    const loadingScreen = document.getElementById('loadingScreen');
    const resultsContainer = document.getElementById('results');


    // 검색 요청을 처리하는 함수
    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();  // 기본 폼 동작 막기
        const searchInputValue = searchInput.value;

        if (!searchInputValue) {
            alert("검색어를 입력하세요!");
            return;
        }

        // 로딩 화면 표시
        loadingScreen.style.display = 'flex';
        resultsContainer.innerHTML = '';

        const formData = new URLSearchParams();
        formData.append('search_input', searchInputValue);

        fetch('/search/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        })
        .then(response => response.text())
        .then(html => {
            // 로딩 화면 숨기기
            loadingScreen.style.display = 'none';
            // 결과 페이지 내용으로 현재 페이지 업데이트
            document.body.innerHTML = html;
            // 스크립트 재실행을 위해 페이지에 스크립트 태그 추가
            const script = document.createElement('script');
            script.src = '/static/script.js';
            document.body.appendChild(script);
        })
        .catch(error => {
            console.error('Error during fetch:', error);
            loadingScreen.style.display = 'none';
            alert('Error: ' + error.message);
        });
    });

    // 음성 인식 기능
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = 'ko-KR';

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            searchInput.value = transcript;
            alert(`음성 인식 결과: ${transcript}`);
        };

        recognition.onend = function() {
            console.log('음성 인식이 종료되었습니다.');
        };

        voiceSearchButton.addEventListener('click', () => {
            recognition.start();
            console.log('음성 인식이 시작되었습니다.');
        });
    } else {
        voiceSearchButton.style.display = 'none';
        console.log('음성 인식이 지원되지 않는 브라우저입니다.');
    }
});

// 추천 문장 카드 자동 검색 기능 (전역 함수)
function autoSearch(searchTerm) {
    document.getElementById('searchInput').value = searchTerm;
    document.getElementById('searchForm').dispatchEvent(new Event('submit'));
}