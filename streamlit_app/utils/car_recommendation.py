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

    if user["preferred_type"] == car["car_type"]:
        score += 5
    if user["preferred_fuel"] == car["fuel_type"]:
        score += 3

    # ✅ 가격이 범위 안에 들어오는 경우 점수 부여
    price = pd.to_numeric(car["price"], errors="coerce")
   
    if not pd.isna(price) and user["budget_min"] <= price <= user["budget_max"]:
        score += 2
    if user["num_kids"] >= 2 and car["car_type"] in ["SUV", "대형", "MPV"]:
        score += 3

    korean_brands = ["현대", "기아", "제네시스", "쉐보레", "쌍용", "르노삼성"]
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
            "기본점수": b_score,
            "신뢰도점수": t_score,
            "총점": total
        })

    return pd.DataFrame(results).sort_values(by="총점", ascending=False).reset_index(drop=True)

# ✅ 테스트용 실행 (단독 실행 시 사용)
if __name__ == "__main__":
    df = get_recommendations(user)
    print(df.head(10))
