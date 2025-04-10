import pandas as pd
from utils.db import get_connection  # DB 연결 함수 가져오기
# from db import get_connection  # DB 연결 함수 가져오기

#  사용자 조건
user = {
    "preferred_type": "SUV",
    "preferred_fuel": "디젤",
    "budget_min": 3000,
    "budget_max": 5000,
    "brand_origin": "국산",
    "num_kids": 2
}

# ✅ 기본 적합도 점수 함수
def basic_score(user, car):
    score = 0
    preferred_type = user["preferred_type"]
    car_type = car["car_type"]
    
    truck_types = ["경트럭", "소형트럭", "중형트럭"]
    special_types = ["소형버스", "픽업/밴", "승합"]

    # ✅ 차종에 따른 가중치 조정
    if preferred_type in truck_types:
        if preferred_type == car_type:
            score += 9  # 정확히 일치하는 트럭
        elif car_type in truck_types:
            score += 3   # 같은 트럭 계열이지만 다름
        else:
            score -= 5   # 트럭 선호자지만 트럭이 아님

    elif preferred_type in special_types: # 특수 차종(픽업/밴, 소형버스 등)
        if preferred_type == car_type:
            score += 5
        else:
            score -= 5

    else:
        if car_type in truck_types or car_type in special_types:
            score -= 5     # 트럭이나 특수차종에게는 마이너스
        elif preferred_type == car_type:
            score += 5     # 일반적인 차종 선호와 일치
        else:
            score += 2      # 다른 차종이지만 비슷한 카테고리 (SUV, 세단 등)


    # ✅ 연료 타입 선호
    if user["preferred_fuel"] == car["fuel_type"]:
        score += 1

    # ✅ 예산 범위
    price = pd.to_numeric(car["price"], errors="coerce")
    if not pd.isna(price):
        if user["budget_min"] <= price <= user["budget_max"]:
            score += 3
        elif price < user["budget_min"]:
            score += 2
        else:
            minscore = (user['budget_max'] / price)
            score -= minscore
            
    # ✅ 자녀 수에 따른 대형차 선호
    if user["num_kids"] >= 2 and car_type in ["SUV", "대형", "MPV"]:
        score += 1

    # ✅ 브랜드 선호 (국산 vs 해외)
    korean_brands = ["기아", "대창모터스", "디피코", "모빌리티네트웍스", "쎄보모빌리티",
                     "이비온", "자일자동차", "제네시스", "제이스모빌리티", "현대"]
    
    if user["brand_origin"] == "국산" and car["brand"] in korean_brands:
        score += 2
    elif user["brand_origin"] == "해외" and car["brand"] not in korean_brands:
        score += 2

    return score
# ✅ 리콜 기반 신뢰도 점수 함수
def trust_score(recalls_df, brand, name):
    entries = recalls_df[(recalls_df["brand"] == brand) & (recalls_df["name"] == name)]
    base_score = 10
    penalty = 0

    recall_type_weights = {"자발적리콜": 1, "제작결함": 2}
    critical_keywords = ["브레이크", "엔진", "화재", "전기", "제동", "조향", "누유"]

    for _, row in entries.iterrows():
        weight = recall_type_weights.get(row["recall_type"], 2)
        defect = str(row["defect_description"])
        keyword_penalty = sum(1 for kw in critical_keywords if kw in defect)
        penalty += weight + keyword_penalty

    return max(base_score - penalty, 0)

# ✅ 차량 추천 함수 (Streamlit에서 호출 가능)
def get_recommendations(user):

    engine = get_connection()
    #  데이터 불러오기
    cars_df = pd.read_sql("SELECT * FROM cars", engine)
    recalls_df = pd.read_sql("SELECT * FROM recalls", engine)

    results = []

    for _, car in cars_df.iterrows():
        b_score = basic_score(user, car)
        t_score = trust_score(recalls_df, car["brand"], car["name"])
        total = b_score + t_score
        results.append({
            "모델명": car["name"],
            "브랜드": car["brand"],
            "연료": car["fuel_type"],
            "차종": car["car_type"],
            "가격": car["price"],
            "이미지" : car["image_url"],
            "기본점수": b_score,
            "신뢰도점수": t_score,
            "총점": total
        })

    return pd.DataFrame(results).sort_values(by="총점", ascending=False).reset_index(drop=True)

# ✅ 테스트용 실행 (단독 실행 시 사용)
if __name__ == "__main__":
    df = get_recommendations(user)
    print(df.head(10))
