import streamlit as st
import pandas as pd
from utils.db import get_connection
from sqlalchemy import text

POSTS_PER_PAGE = 5

def get_faq_data():
    engine = get_connection()
    with engine.connect() as conn:
        query = text("SELECT question AS 질문, answer AS 답변 FROM car_faq")
        result = conn.execute(query)
        return result.mappings().all()  # 바로 리스트로 변환


def show():
    st.title("❓ FAQ")
    st.write("차량 관련 자주 묻는 질문과 답변을 확인하세요!")

    faq_data = get_faq_data()
    total_posts = len(faq_data)
    total_pages = (total_posts - 1) // POSTS_PER_PAGE + 1

    if "faq_page" not in st.session_state:
        st.session_state.faq_page = 1

    current_page = st.session_state.faq_page
    start_idx = (current_page - 1) * POSTS_PER_PAGE
    end_idx = start_idx + POSTS_PER_PAGE
    page_data = faq_data[start_idx:end_idx]  # ✅ 슬라이싱 가능

    for row in page_data:
        with st.expander(f"Q. {row['질문']}"):
            st.write(f"👉 {row['답변']}")

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 8, 1])

    with col1:
        if current_page > 1:
            if st.button("⬅&nbsp;&nbsp;&nbsp;&nbsp;이전"):
                st.session_state.faq_page -= 1
                st.rerun()

    with col2:
        st.markdown(
            f"<div style='text-align:center;'>페이지 {current_page} / {total_pages}</div>",
            unsafe_allow_html=True
        )

    with col3:
        if current_page < total_pages:
            if st.button("다음&nbsp;&nbsp;&nbsp;&nbsp;➡"):
                st.session_state.faq_page += 1
                st.rerun()
