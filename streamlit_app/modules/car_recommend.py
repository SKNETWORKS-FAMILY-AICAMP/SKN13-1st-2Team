# car_recommend.py

import streamlit as st
import pandas as pd
from utils.car_recommendation import get_recommendations
from utils.db import get_connection

def show():
    st.title("🚗 차량 조건을 선택하세요")
    st.write("이 정보는 차의 선호도 순위와 결함 정보를 통해 작성되었습니다!")

    # ✅ hover 효과용 스타일
    st.markdown("""
        <style>
        .card {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 6px;
            background-color: #fff;
            height: 300px;  /* ✅ 유지 */
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: flex-start;
            transition: all 0.2s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .car-image {
            width: 100%;
            height: 140px;
            object-fit: contain;
            border-radius: 5px;
            margin-bottom: 6px;
        }
        .car-title {
            margin: 4px 0;
            font-size: 14px;
            font-weight: bold;
        }
        .car-info {
            margin: 2px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # ✅ DB 연결
    engine = get_connection()
    cars_df = pd.read_sql("SELECT * FROM cars", engine)

    # ✅ 슬라이더 및 필터
    price_min = 1000
    price_max = 10000
    real_max_price = int(pd.to_numeric(cars_df["price"], errors="coerce").max())

    car_types = sorted(cars_df["car_type"].dropna().unique())
    fuel_types = sorted(cars_df["fuel_type"].dropna().unique())

    with st.form("car_conditions"):
        st.markdown("#### 💡 조건 입력")
        price_range = st.slider("가격대 (만원)", min_value=price_min, max_value=price_max, value=(3000, 5000), step=500)
        adjusted_max_price = real_max_price if price_range[1] >= price_max else price_range[1]

        col1, col2 = st.columns(2)
        with col1:
            car_type = st.selectbox("차종", ["(선택 안 함)"] + list(car_types))
        with col2:
            fuel_type = st.selectbox("연료 타입", ["(선택 안 함)"] + list(fuel_types))

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

        top_5 = result_df[["모델명", "브랜드", "연료", "차종", "가격", "이미지"]].head(5)

        st.markdown("### 🌟 추천 차량")
        cols = st.columns(5)
        for idx, (_, row) in enumerate(top_5.iterrows()):
            # 가격 포맷팅: 억 단위 처리
            try:
                price_val = int(row['가격'])
                if price_val >= 10000:
                    eok = price_val // 10000
                    man = price_val % 10000
                    if man == 0:
                        formatted_price = f"{eok}억"
                    else:
                        formatted_price = f"{eok}억 {man:,}만원"
                else:
                    formatted_price = f"{price_val:,}만원"
            except:
                formatted_price = row['가격']  # 혹시 오류 시 원본 표시

            with cols[idx]:
                st.markdown(f"""
                    <div class="card">
                        <img src="{row['이미지']}" class="car-image">
                        <h5 class="car-title">{idx+1}위: {row['모델명']}</h5>
                        <p class="car-info">&nbsp;&nbsp;{row['연료']}</p>
                        <p class="car-info">&nbsp;&nbsp;{row['차종']}</p>
                        <p class="car-info">&nbsp;&nbsp;{formatted_price}</p>
                    </div>
                """, unsafe_allow_html=True)
