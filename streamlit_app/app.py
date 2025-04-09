import streamlit as st
from streamlit_option_menu import option_menu

# 페이지 모듈 import
from modules import car_view, car_recommend, recall_info, faq

# 페이지 설정
st.set_page_config(page_title="신차 검색 서비스", layout="wide")

# ✅ 사이드바 메뉴 구성 (세션 상태 제거)
with st.sidebar:
    selected = option_menu(
        "신차 검색 서비스",
        ["차량 보기", "추천 차량", "결함 정보", "FAQ"],
        icons=["search", "stars", "exclamation-triangle", "question-circle"],
        menu_icon="car-front",
        default_index=0,
        styles={
            "container": {"padding": "4!important"},
            "icon": {"font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px"},
            "nav-link-selected": {"background-color": "#F28500"},
        }
    )

# ✅ 라우팅 처리
if selected == "차량 보기":
    car_view.show()
elif selected == "추천 차량":
    car_recommend.show()
elif selected == "결함 정보":
    recall_info.show()
elif selected == "FAQ":
    faq.show()
