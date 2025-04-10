import streamlit as st
import pandas as pd
from utils.db import get_connection

POSTS_PER_PAGE = 5


def get_faq_data():
    conn = get_connection()
    query = "SELECT question AS 질문, answer AS 답변 FROM car_faq"
    return pd.read_sql(query, conn)

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
    page_data = faq_data[start_idx:end_idx].to_dict(orient="records")
    print(page_data)
    for row in page_data:
        with st.expander(f"Q. {row['질문']}"):
            st.write(f"👉 {row['답변']}")

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if current_page > 1:
            if st.button("⬅️ 이전"):
                st.session_state.faq_page -= 1

    with col2:
        st.markdown(f"<div style='text-align:center;'>📄 페이지 {current_page} / {total_pages}</div>", unsafe_allow_html=True)

    with col3:
        if current_page < total_pages:
            if st.button("다음 ➡️"):
                st.session_state.faq_page += 1
