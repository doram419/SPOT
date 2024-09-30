document.addEventListener("DOMContentLoaded", function() {
    // 슬라이더 관련 DOM 요소
    const sliderWrapper = document.getElementById('sliderWrapper');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    let currentIndex = 0;

    // 슬라이더 아이템 개수
    const totalItems = document.querySelectorAll('.slider-item').length;

    // 슬라이드 이동 함수
    function moveSlider(index) {
        const slideWidth = sliderWrapper.querySelector('.slider-item').clientWidth;
        sliderWrapper.style.transform = `translateX(${-index * slideWidth}px)`;
    }

    // 이전 버튼 클릭
    prevBtn.addEventListener('click', function() {
        if (currentIndex > 0) {
            currentIndex--;
            moveSlider(currentIndex);
        }
    });

    // 다음 버튼 클릭
    nextBtn.addEventListener('click', function() {
        if (currentIndex < totalItems - 1) {
            currentIndex++;
            moveSlider(currentIndex);
        }
    });
});
