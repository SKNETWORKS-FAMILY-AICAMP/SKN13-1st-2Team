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

# --- Streamlit 페이지 ---
def show():
    st.title("🚘 차량 브랜드 보기")
    brands_df = get_brands()
    selected_brand = None

    for i in range(0, len(brands_df), 16):
        cols = st.columns(16)
        for j in range(16):
            if i + j < len(brands_df):
                brand = brands_df.iloc[i + j]
                with cols[j]:
                    if st.button(" ", key=brand["brand"]):
                        selected_brand = brand["brand"]
                    st.image(brand["brand_img"], width=50, use_container_width=False)
                    st.markdown(
                        f"<div style='text-align:center; font-size:11px; margin-top:4px; color:#ccc'>{brand['brand']}</div>",
                        unsafe_allow_html=True
                    )

    if selected_brand:
        st.markdown(f"### 🚗 {selected_brand} 차량 목록")
        cars_df = get_cars_by_brand(selected_brand)
        cols = st.columns(5)
        for i, (_, car) in enumerate(cars_df.iterrows()):
            col = cols[i % 5]
            with col:
                st.markdown(
                    f"""
                    <a href="{car['detail_url']}" target="_blank">
                        <img src="{car['image_url']}" width="100" style="border-radius:10px;"/>
                    </a>
                    <div style="text-align:center; font-size:12px; margin-top:5px;">{car['car_name']}</div>
                    """,
                    unsafe_allow_html=True
                )
