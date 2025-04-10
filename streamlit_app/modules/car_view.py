import streamlit as st
import pandas as pd
from PIL import Image
from utils.db import get_connection

@st.cache_data
def get_brands():
    engine = get_connection()
    df = pd.read_sql("SELECT * FROM car_brands", engine)
    return df

@st.cache_data
def get_cars_by_brand(brand_name):
    engine = get_connection()
    query = "SELECT * FROM cars WHERE brand = %s"
    df = pd.read_sql(query, engine, params=(brand_name,))
    return df

@st.cache_data
def get_all_cars():
    engine = get_connection()
    df = pd.read_sql("SELECT * FROM cars", engine)
    return df

# --- Streamlit 페이지 ---
def show():
    st.title("🚘 차량 브랜드 보기")

    # --- 세션 상태 초기화 ---
    if "selected_brand" not in st.session_state:
        st.session_state.selected_brand = None

    brands_df = get_brands()

# --- 브랜드 로고 출력 ---
    st.markdown("### 🌟 브랜드 선택")
    for i in range(0, len(brands_df), 16):
        cols = st.columns(16)
        for j in range(16):
            if i + j < len(brands_df):
                brand = brands_df.iloc[i + j]
                with cols[j]:
                    # 로고를 테두리에 맞게 감싸고 클릭 가능하게 form 활용
                    form_key = f"form_{brand['brand']}"
                    with st.form(form_key):
                        st.markdown(
                            f"""
                            <div style="text-align:center;">
                                <div style="
                                    display:inline-block;
                                    width:45px;
                                    height:45px;
                                    border:1px solid #ccc;
                                    border-radius:8px;
                                    overflow:hidden;
                                    padding:2px;
                                    box-sizing:border-box;
                                ">
                                    <img src="{brand['brand_img']}" style="width:45px; height:45px;" />
                                </div>
                                <div style="font-size:11px; margin-top:4px; color:#777;">{brand['brand']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        if st.form_submit_button(" ", use_container_width=True):
                            st.session_state.selected_brand = brand['brand']
                        
    # --- 전체보기 초기화 버튼 ---
    st.markdown(" ")
    if st.session_state.selected_brand:
        if st.button("🔄 전체 차량 보기"):
            st.session_state.selected_brand = None

    # --- 차량 리스트 출력 ---
    if st.session_state.selected_brand:
        st.markdown(f"### 🚗 {st.session_state.selected_brand} 차량 리스트")
        cars_df = get_cars_by_brand(st.session_state.selected_brand)
    else:
        st.markdown("### 🌟 전체 차량 리스트")
        cars_df = get_all_cars()

    # --- 카드 스타일로 차량 보여주기 ---
    cols = st.columns(3)
    for i, (_, car) in enumerate(cars_df.iterrows()):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div style="text-align:center; border:1px solid #ddd; border-radius:12px; padding:10px; margin-bottom:20px;">
                    <img src="{car['image_url']}" style="width:100%; height:auto; border-radius:10px;" />
                    <div style="font-size:15px; font-weight:bold; margin-top:8px;">{car['name']}</div>
                    <div style="font-size:13px; color:#666;">연료: {car['fuel_type']}</div>
                    <div style="font-size:13px; color:#000; font-weight:bold;">가격: {car['price']}만원</div>
                </div>
                """,
                unsafe_allow_html=True
            )
