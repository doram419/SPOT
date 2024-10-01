const recommendations = [
    "서초동 분위기 좋은 카페",
    "남자 4명이서 가는 가성비 있는 강남역 고깃집",
    "부모님과 갈 만한 송파동 식당",
    "썸남과 갈만한 분위기 좋은 잠실 맛집",
    "홍대 데이트 코스",
    "이태원 브런치 맛집",
    "강남 직장인 회식 장소",
    "한강공원 근처 피크닉 스팟",
    "을지로 힙한 카페",
    "성수동 인스타 감성 카페",
    "광화문 역사 투어 코스",
    "청담동 럭셔리 다이닝",
    "종로 전통 한식당",
    "명동 쇼핑 후 식사할 곳",
    "여의도 한강뷰 레스토랑"
];

function getRandomRecommendations(count) {
    const shuffled = recommendations.sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
}

function renderRecommendationCards() {
    const cardContainer = document.getElementById('cardContainer');
    const randomRecommendations = getRandomRecommendations(4);
    
    cardContainer.innerHTML = randomRecommendations.map(rec => `
        <div class="card" onclick="autoSearch('${rec}')">
            <div class="icon"></div>
            ${rec}
        </div>
    `).join('');
}