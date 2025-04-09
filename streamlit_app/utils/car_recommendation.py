
import pandas as pd
import pymysql

# 1. MySQL 연결 설정
conn = pymysql.connect(
    host='localhost',
    user='your_username',
    password='your_password',
    db='car_data',
    charset='utf8'
)

# 2. 데이터 불러오기
cars_df = pd.read_sql("SELECT * FROM cars", conn)
recalls_df = pd.read_sql("SELECT * FROM recalls", conn)

# 3. 사용자 조건
user = {
    "preferred_type": "SUV",
    "preferred_fuel": "디젤",
    "budget_min": 3000,
    "budget_max": 5000,
    "brand_origin": "국산",
    "num_kids": 2
}

# 4. 기본 적합도 점수
def basic_score(user, car):
    score = 0

    if user["preferred_type"] == car["car_type"]:
        score += 5
    if user["preferred_fuel"] == car["fuel_type"]:
        score += 3

    # ✅ 가격이 범위 안에 들어오는 경우 점수 부여
    if car["price"] is not None and user["budget_min"] <= car["price"] <= user["budget_max"]:
        score += 2

    # 자녀 수가 많으면 SUV 등 가산점
    if user["num_kids"] >= 2 and car["car_type"] in ["SUV", "대형", "MPV"]:
        score += 3

    # 국산/해외 선호도 반영
    korean_brands = ["현대", "기아", "제네시스", "쉐보레", "쌍용", "르노삼성"]

    if user["brand_origin"] == "국산" and car["brand"] in korean_brands:
        score += 2
    elif user["brand_origin"] == "해외" and car["brand"] not in korean_brands:
        score += 2

    return score


# 5. 신뢰도 점수
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

# 6. 추천 함수
def get_recommendations(user, cars_df, recalls_df):
    result = []

    for _, car in cars_df.iterrows():
        b_score = basic_score(user, car)
        t_score = trust_score(recalls_df, car["brand"], car["name"])
        total = b_score + t_score

        result.append({
            "model_id": car["model_id"],
            "name": car["name"],
            "brand": car["brand"],
            "total_score": total,
            "basic_score": b_score,
            "trust_score": t_score,
            "price": car["price"],
            "fuel_type": car["fuel_type"],
            "car_type": car["car_type"]
        })

    return pd.DataFrame(result).sort_values(by="total_score", ascending=False)

# 7. 실행
if __name__ == "__main__":
    recommend_df = get_recommendations(user, cars_df, recalls_df)
    print(recommend_df.head(10))
