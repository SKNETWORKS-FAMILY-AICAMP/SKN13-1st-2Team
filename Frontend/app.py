import streamlit as st
from streamlit_option_menu import option_menu

# 페이지 모듈 import
from pages import car_view, car_recommend, recall_info, faq

# 페이지 설정
st.set_page_config(page_title="신차 검색 서비스", layout="wide")

# 세션 상태 초기화
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "차량 보기"

# ✅ 사이드바 메뉴 구성 (기존 스타일 반영)
with st.sidebar:
    selected = option_menu(
        "신차 검색 서비스",
        ["차량 보기", "추천 차량", "결함 정보", "FAQ"],
        icons=["search", "stars", "exclamation-triangle", "question-circle"],
        menu_icon="car-front",
        default_index=0 if st.session_state.current_page == "차량 보기" else 1,
        styles={
            "container": {"padding": "4!important"},
            "icon": {"font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px"},
            "nav-link-selected": {"background-color": "#5bc0de"},
        }
    )

# 현재 선택값 저장
st.session_state["current_page"] = selected

# 라우팅 처리
if selected == "차량 보기":
    car_view.show()
elif selected == "추천 차량":
    car_recommend.show()
elif selected == "결함 정보":
    recall_info.show()
elif selected == "FAQ":
    faq.show()
