document.addEventListener("DOMContentLoaded", function() {
    const voiceSearchButton = document.getElementById('voiceSearchButton');
    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');

    // 음성 인식 기능
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = 'ko-KR';

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            searchInput.value = transcript;
            searchForm.submit();
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
    
    // 페이지 로드 시 추천 카드 렌더링
    renderRecommendationCards();

    // 추천 문장 카드 자동 검색 기능 (전역 함수)
    window.autoSearch = function(searchTerm) {
        searchInput.value = searchTerm;
        searchForm.submit();
    };
});
