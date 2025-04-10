import streamlit as st
import pandas as pd
from utils.car_recommendation import get_recommendations
from utils.db import get_connection

def show():
    st.title("🚗 차량 조건을 선택하세요")

    # ✅ DB 연결 및 고유값 추출
    engine = get_connection()
    cars_df = pd.read_sql("SELECT * FROM cars", engine)

    # ✅ 슬라이더용 범위 설정
    price_min = 1000
    price_max = 10000
    real_max_price = int(pd.to_numeric(cars_df["price"], errors="coerce").max())

    car_types = sorted(cars_df["car_type"].dropna().unique())
    fuel_types = sorted(cars_df["fuel_type"].dropna().unique())

    with st.form("car_conditions"):
        st.markdown("#### 💡 조건 입력")

        # ✅ 가격대 슬라이더
        price_range = st.slider(
            "가격대 (천 만원)",
            min_value=price_min,
            max_value=(price_max),
            value=(3000, 5000),
            step=500
        )  


        # ✅ 10000+ 처리
        adjusted_max_price = real_max_price if price_range[1] >= price_max else price_range[1]

        col1, col2 = st.columns(2)
        with col1:
            car_type = st.selectbox("차종", [""] + list(car_types))
        with col2:
            fuel_type = st.selectbox("연료 타입", [""] + list(fuel_types))

        col3, col4 = st.columns(2)
        with col3:
            brand_origin = st.radio("브랜드 선호", ["국산", "해외"], horizontal=True)
        with col4:
            num_kids = st.slider("자녀 수", 0, 5, 2)

        submitted = st.form_submit_button("🚀 추천 받기")

    if submitted:
        user_input = {
            "preferred_type": car_type,
            "preferred_fuel": fuel_type,
            "budget_min": price_range[0],
            "budget_max": adjusted_max_price,
            "brand_origin": brand_origin,
            "num_kids": num_kids
        }

        st.success("✅ 조건이 적용되었습니다. 추천 차량 리스트를 확인하세요.")
        result_df = get_recommendations(user_input)

        # ✅ 점수 컬럼 제거 및 상위 5개만 추출
        display_df = result_df[["모델명", "브랜드", "연료", "차종", "가격"]].head(5)
        display_df.index = [f"{i+1}위" for i in range(len(display_df))]

        st.dataframe(display_df, use_container_width=True)
