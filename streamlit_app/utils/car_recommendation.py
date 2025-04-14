import pandas as pd
from utils.db import get_connection
from utils.config import (
    RECALL_TYPE_WEIGHTS,
    CRITICAL_KEYWORDS,
    KOREAN_BRANDS,
    TRUCK_TYPES,
    SPECIAL_TYPES,
    FAMILY_FRIENDLY_TYPES
)

#  사용자 조건
user = {
    "preferred_type": "SUV",
    "preferred_fuel": "가솔린",
    "budget_min": 2000,
    "budget_max": 4000,
    "brand_origin": "해외",
    "num_kids": 0
}

def calculate_type_score(preferred_type: str, car_type: str) -> float:
    """차종 점수를 계산합니다."""
    if preferred_type is None:
        return 0
    
    if preferred_type == "SUV":
        if car_type == "SUV":
            return 8  # SUV 선호도 크게 증가
        elif car_type in ["경형SUV", "대형SUV"]:
            return 6  # 비슷한 차종에 대한 점수도 증가
        elif car_type in TRUCK_TYPES or car_type in SPECIAL_TYPES:
            return -3
        return 0
    elif preferred_type in TRUCK_TYPES:
        if preferred_type == car_type:
            return 9
        elif car_type in TRUCK_TYPES:
            return 3
        return -5
    elif preferred_type in SPECIAL_TYPES:
        return 5 if preferred_type == car_type else -5
    else:
        if car_type in TRUCK_TYPES or car_type in SPECIAL_TYPES:
            return -5
        return 5 if preferred_type == car_type else 2

def calculate_budget_score(user: dict, price: float) -> float:
    """예산 범위에 따른 점수를 계산합니다."""
    if pd.isna(price) or user["budget_min"] is None or user["budget_max"] is None:
        return 0
    
    budget_mid = (user["budget_min"] + user["budget_max"]) / 2
    if user["budget_min"] <= price <= user["budget_max"]:
        # 예산 범위 내에서 중간값과의 거리에 따라 더 세밀한 점수 계산
        distance_from_mid = abs(price - budget_mid)
        range_size = (user["budget_max"] - user["budget_min"]) / 2
        normalized_distance = distance_from_mid / range_size
        return 5.5 * (1 - normalized_distance**2)  # 제곱함수로 더 부드러운 감소
    elif price < user["budget_min"]:
        # 예산 미달시 거리에 따른 점수 감소
        ratio = price / user["budget_min"]
        return 2.5 * ratio**1.5  # 지수 함수로 더 부드러운 증가
    else:
        # 예산 초과시 더 큰 감점
        ratio = price / user["budget_max"]
        return -3.5 * (ratio - 1)**1.2  # 지수 함수로 더 부드러운 감소

def calculate_brand_score(user: dict, car_brand: str) -> float:
    """브랜드 원산지에 따른 점수를 계산합니다."""
    if user["brand_origin"] is None:
        return 0
    
    is_korean = car_brand in KOREAN_BRANDS
    premium_brands = {"제네시스", "기아"}  # 프리미엄 브랜드 목록
    
    base_score = 0
    if user["brand_origin"] == "국산":
        if is_korean:
            base_score = 3.25  # 기본 국산차 점수
            if car_brand in premium_brands:
                base_score += 0.75  # 프리미엄 브랜드 추가 점수
        else:
            base_score = -1.5
    else:  # 해외 선호
        if not is_korean:
            base_score = 3.25
        else:
            base_score = -1.5
    
    return base_score

def calculate_family_score(user: dict, car: dict) -> float:
    """가족 친화도 점수를 계산합니다."""
    if user["num_kids"] is None or user["num_kids"] == 0:
        return 0
        
    car_type = car["car_type"]
    if car_type in FAMILY_FRIENDLY_TYPES:
        if user["num_kids"] >= 3:
            return 4.25  # 대가족에 적합
        elif user["num_kids"] >= 2:
            return 3.25  # 중형 가족에 적합
        else:
            return 2.25  # 소형 가족에 적합
    return -0.75  # 가족용으로 부적합한 경우 약간의 감점

def calculate_fuel_score(user: dict, car_fuel: str) -> float:
    """연료 타입에 따른 점수를 계산합니다."""
    if user["preferred_fuel"] is None or car_fuel is None:
        return 0
        
    car_fuels = [f.strip() for f in car_fuel.split(',')]
    
    # 선호 연료가 포함된 경우
    if user["preferred_fuel"] in car_fuels:
        score = 5.25  # 기본 선호 연료 점수
        if len(car_fuels) > 1:
            score += 0.25  # 다중 연료 옵션 보너스
        return score
    
    # 비선호 연료에 대한 세분화된 감점
    if '전기(배터리)' in car_fuels and user["preferred_fuel"] != '전기(배터리)':
        return -3.25
    elif '하이브리드' in car_fuels and user["preferred_fuel"] != '하이브리드':
        return -2.25
    elif 'LPG' in car_fuels and user["preferred_fuel"] != 'LPG':
        return -1.75
    return -1.25

def basic_score(user: dict, car: dict) -> float:
    """기본 점수를 계산합니다."""
    weights = {
        'type': 1.5,    # 차종 선호도 가중치 크게 증가
        'fuel': 1.2,    # 연료 타입의 중요도
        'budget': 1.0,  # 예산 기준 중요도
        'family': 0.7,  # 가족 친화도
        'brand': 0.9    # 브랜드 중요도
    }
    
    raw_scores = {
        'type': calculate_type_score(user["preferred_type"], car["car_type"]),
        'fuel': calculate_fuel_score(user, car["fuel_type"]),
        'budget': calculate_budget_score(user, pd.to_numeric(car["price"], errors="coerce")),
        'family': calculate_family_score(user, car),
        'brand': calculate_brand_score(user, car["brand"])
    }
    
    # 각 카테고리별 가중 점수 계산
    weighted_scores = {k: weights[k] * v for k, v in raw_scores.items()}
    
    # 총점 계산 (정규화 없이 원본 점수 범위 유지)
    total = sum(weighted_scores.values())
    
    # 점수가 음수가 되지 않도록 보정
    return max(total, 0)

def get_recommendations(user: dict) -> pd.DataFrame:
    """사용자 조건에 맞는 차량을 추천합니다."""
    # 입력 유효성 검사
    required_fields = ["preferred_type", "preferred_fuel", "budget_min", "budget_max", "brand_origin", "num_kids"]
    if not all(field in user for field in required_fields):
        raise ValueError(f"Missing required user preferences: {required_fields}")
    
    # "(선택 안 함)" 값을 None으로 변환
    if user["preferred_type"] == "(선택 안 함)":
        user["preferred_type"] = None
    if user["preferred_fuel"] == "(선택 안 함)":
        user["preferred_fuel"] = None
    
    engine = get_connection()
    cars_df = pd.read_sql("SELECT * FROM cars", engine)
    recalls_df = pd.read_sql("SELECT * FROM recalls", engine)

    def calculate_scores(car: dict) -> dict:
        """각 차량의 점수를 계산합니다."""
        b_score = basic_score(user, car)
        
        # 리콜 점수 계산 로직 세분화
        entries = recalls_df[(recalls_df["brand"] == car["brand"]) & (recalls_df["name"] == car["name"])]
        recall_penalty = sum(
            RECALL_TYPE_WEIGHTS.get(row["recall_type"], 2) * 1.2 +  # 기본 리콜 가중치 증가
            sum(1.5 for kw in CRITICAL_KEYWORDS if kw in str(row["defect_description"]))  # 중요 결함 가중치 증가
            for _, row in entries.iterrows()
        )
        
        # 리콜 점수를 0-8 범위로 조정 (기본점수와의 밸런스를 위해)
        t_score = max(8 - recall_penalty, 0)
        
        # 최종 점수 계산 시 소수점 3자리까지 유지
        final_score = round(b_score + t_score, 3)
        
        return {
            "모델명": car["name"],
            "브랜드": car["brand"],
            "연료": car["fuel_type"],
            "차종": car["car_type"],
            "가격": car["price"],
            "이미지": car["image_url"],
            "기본점수": round(b_score, 3),
            "신뢰도점수": round(t_score, 3),
            "총점": final_score
        }

    results = [calculate_scores(car) for _, car in cars_df.iterrows()]
    return pd.DataFrame(results).sort_values(by="총점", ascending=False).reset_index(drop=True)

if __name__ == "__main__":
    df = get_recommendations(user)
    print(df.head(10))
