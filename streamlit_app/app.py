import streamlit as st
from streamlit_option_menu import option_menu

# 페이지 모듈 import
from modules import car_view, car_recommend, recall_info, faq


# 페이지 설정
st.set_page_config(page_title="신차 검색 서비스", layout="wide")

st.markdown("""
    <style>
    /* 사이드바 배경 */
    section[data-testid="stSidebar"] {
        background-color: #fef4e3;  /* 흰색 유지 */
    }

    /* 사이드바 제목 */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #fef4e3;  /* 주황색 */
    }

    /* 버튼 스타일 (예: 차량 보기) */
    div.stButton > button {
        background-color: #fef4e3;
        color: black;
        border: none;
        border-radius: 8px;
        padding: 0.5em 1em;
    }

    /* 버튼 호버 스타일 */
    div.stButton > button:hover {
        background-color: #F28500;
        color: white;
    }

    /* 선택된 텍스트 강조 색상 */
    .css-1v0mbdj {
        color: #f57c00;
    }
    </style>
""", unsafe_allow_html=True)


# ✅ 사이드바 메뉴 구성 (세션 상태 제거)
with st.sidebar:
    # 👉 사이드바 너비 안에서 3등분해서 가운데 칼럼에만 이미지 배치
    col1, col2, col3 = st.columns([1, 8, 1])  # 비율 조절 가능
    with col2:
        st.image("img/drmc_logo.png", width=200)
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
