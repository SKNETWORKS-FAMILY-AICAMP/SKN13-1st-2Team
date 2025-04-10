import streamlit as st
import pandas as pd
from utils.db import get_connection

@st.cache_data
def get_brands():
    engine = get_connection()
    return pd.read_sql("SELECT * FROM car_brands", engine)

@st.cache_data
def get_cars_by_brand(brand_name):
    engine = get_connection()
    return pd.read_sql("SELECT * FROM cars WHERE brand = %s", engine, params=(brand_name,))

@st.cache_data
def get_all_cars():
    engine = get_connection()
    return pd.read_sql("SELECT * FROM cars", engine)

def show():
    st.title("🚘 차량 브랜드 보기")

    # --- 클릭 처리용 URL 파라미터 추출 ---
    query_params = st.query_params
    clicked_brand = query_params.get("brand")

    if clicked_brand:
        st.session_state.selected_brand = clicked_brand
    elif "selected_brand" not in st.session_state:
        st.session_state.selected_brand = None

    brands_df = get_brands()

    st.markdown("""
    <style>
    .brand-btn {
        background-color: white;
        border: 1px solid #ccc;
        border-radius: 8px;
        padding: 4px;
        width: 90px;
        height: 65px;
        text-align: center;
        font-size: 10px;
        color: #333;
        margin: 2px auto;
    }
    .brand-btn:hover {
        background-color: #f0f0f0;
        cursor: pointer;
    }
    .brand-btn img {
        width: 30px;
        height: 30px;
        margin-bottom: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### 🌟 브랜드 선택")

    for i in range(0, len(brands_df), 11):
        cols = st.columns(11)
        for j in range(11):
            if i + j < len(brands_df):
                brand = brands_df.iloc[i + j]
                with cols[j]:
                    html = f"""
                    <form action="" method="get">
                        <input type="hidden" name="brand" value="{brand['brand']}"/>
                        <button type="submit" class="brand-btn">
                            <img src="{brand['brand_img']}"/>
                            <div>{brand['brand']}</div>
                        </button>
                    </form>
                    """
                    st.markdown(html, unsafe_allow_html=True)

    # 전체 보기 버튼
    if st.session_state.get("selected_brand"):
        st.write("")
        st.write("")
        if st.button("🔄 전체 차량 보기"):
            st.session_state.selected_brand = None
            st.query_params.clear()  # URL 초기화

    # 차량 리스트
    if st.session_state.get("selected_brand"):
        st.write("")
        st.write("")
        st.markdown(f"### 🚗 {st.session_state.selected_brand} 차량 리스트")
        cars_df = get_cars_by_brand(st.session_state.selected_brand)
    else:
        st.write("")
        st.write("")
        st.markdown("### 🌟 전체 차량 리스트")
        cars_df = get_all_cars()

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
