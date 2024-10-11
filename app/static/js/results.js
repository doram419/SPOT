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
        renderMap(index);
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

    // 지도 렌더링 함수
    function renderMap(index) {

        console.log(`Attempting to render map for index: ${index}`);

        const mapDivId = `map-${index}`;
        const mapElement = document.getElementById(mapDivId);
        const sliderItem = document.querySelectorAll('.slider-item')[index];

        if (!mapElement) {
            console.error(`Map element with ID ${mapDivId} not found`);
            return;
        }
        
        if (mapElement.dataset.rendered !== "true") {
            // 지도 이미 렌더링되었는지 확인 (중복 렌더링 방지)
            mapElement.dataset.rendered = "true";

            mapElement.classList.add('map');

            // 슬라이드 아이템의 데이터 속성에서 위도와 경도 값 가져오기
            const latitude = parseFloat(sliderItem.dataset.latitude);
            const longitude = parseFloat(sliderItem.dataset.longitude);

            console.log(`Latitude: ${latitude}, Longitude: ${longitude}`);

            // 좌표 데이터 디버깅
            if (isNaN(latitude) || isNaN(longitude)) {
                console.error("Invalid latitude or longitude for the map, setting default location.");
                return; // 또는 기본값을 설정하려면:
                // const latitude = 37.5665; // 기본 서울 좌표
                // const longitude = 126.9780;
            }

            // 지도 API를 사용해 지도 생성
            const mapOptions = {
                center: new naver.maps.LatLng(latitude, longitude),
                zoom: 14
            };
            const map = new naver.maps.Map(mapDivId, mapOptions);

            // 마커 추가
            const marker = new naver.maps.Marker({
                position: new naver.maps.LatLng(latitude, longitude),
                map: map
            });
        }
    }

    // 초기 슬라이드에 해당하는 지도 렌더링
    console.log("Rendering initial map for index:", currentIndex);
    renderMap(currentIndex);
});
