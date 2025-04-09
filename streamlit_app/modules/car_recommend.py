import streamlit as st
import pandas as pd
from utils.db import get_connection
from utils.car_recommendation import get_recommendations

def show():
    st.title("🚗 차량 조건을 선택하세요")

    # ✅ DB에서 데이터 불러오기
    conn = get_connection()
    cars_df = pd.read_sql("SELECT * FROM cars", conn)
    recalls_df = pd.read_sql("SELECT * FROM recalls", conn)
    conn.close()

    # ✅ price 컬럼을 숫자로 변환
    cars_df["price"] = pd.to_numeric(cars_df["price"], errors="coerce")
    cars_df = cars_df.dropna(subset=["price"])

    # ✅ (중간 확인) price 컬럼 정보 확인
    st.write("📌 cars_df.columns:", cars_df.columns)
    st.write("📌 price 예시:", cars_df['price'].head(10))
    st.write("📌 price 타입:", cars_df['price'].dtype)
    st.write("📌 price 중 NaN 개수:", cars_df['price'].isnull().sum())

    # ✅ 가격 범위 계산
    min_price = int(cars_df["price"].min())
    max_price = int(cars_df["price"].max())

    # ✅ 고유 차종/연료타입 리스트 추출
    car_types = sorted(cars_df["car_type"].dropna().unique().tolist())
    fuel_types = sorted(cars_df["fuel_type"].dropna().unique().tolist())

    # ✅ 조건 입력 폼
    with st.form("car_conditions"):
        st.markdown("#### 💡 조건 입력")

        price_range = st.slider(
            "가격대 (만원)", 
            min_value=min_price, max_value=max_price, 
            value=(3000, 5000), step=100
        )

        col1, col2 = st.columns(2)
        with col1:
            car_type = st.selectbox("차종", [""] + car_types)
        with col2:
            fuel_type = st.selectbox("연료 타입", [""] + fuel_types)

        col3, col4 = st.columns(2)
        with col3:
            brand_origin = st.radio("브랜드 선호", ["국산", "해외"], horizontal=True)
        with col4:
            num_kids = st.slider("자녀 수", 0, 5, value=2)

        submitted = st.form_submit_button("🚀 추천 받기")

    if submitted:
        user_input = {
            "preferred_type": car_type,
            "preferred_fuel": fuel_type,
            "budget_min": price_range[0],
            "budget_max": price_range[1],
            "brand_origin": brand_origin,
            "num_kids": num_kids
        }

        # 추천 결과 생성
        st.success("✅ 조건이 적용되었습니다. 추천 차량 리스트를 확인하세요.")
        recommend_df = get_recommendations(user_input, cars_df, recalls_df)

        # 결과 출력
        st.dataframe(recommend_df[[
            "brand", "name", "price", 
            "car_type", "fuel_type", 
            "basic_score", "trust_score", "total_score"
        ]].reset_index(drop=True), use_container_width=True)
