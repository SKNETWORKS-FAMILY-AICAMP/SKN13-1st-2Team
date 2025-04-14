"""
Configuration constants for car recommendation system
"""

# Weights for different types of recalls
RECALL_TYPE_WEIGHTS = {
    "자발적리콜": 1,
    "제작결함": 2
}

# Critical keywords for defect descriptions
CRITICAL_KEYWORDS = [
    "브레이크",
    "엔진",
    "화재",
    "전기",
    "제동",
    "조향",
    "누유"
]

# List of Korean car brands
KOREAN_BRANDS = [
    "기아",
    "대창모터스",
    "디피코",
    "모빌리티네트웍스",
    "쎄보모빌리티",
    "에스에스라이트",
    "이비온",
    "자일자동차",
    "제네시스",
    "제이스모빌리티",
    "트라베리",
    "현대"
]

# Vehicle type categories
TRUCK_TYPES = ["경트럭", "소형트럭", "중형트럭"]
SPECIAL_TYPES = ["소형버스", "픽업/밴", "승합"]
FAMILY_FRIENDLY_TYPES = ["SUV", "대형", "MPV"]