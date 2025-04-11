import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import MaxNLocator
import plotly.graph_objects as go
import numpy as np
from sqlalchemy import create_engine
import pymysql
from utils.db import get_connection  # DB 연결 함수 가져오기
import io


# # 한국어 폰트 설정
# matplotlib.rc('font', family='Malgun Gothic')
# matplotlib.rcParams['axes.unicode_minus'] = False

# 브랜드 매핑
BRAND_MAPPING = {
    "bmw": "BMW",
    "kia": "기아",
    "hyundai": "현대",
    "benz": "벤츠",
    "mercedes": "벤츠",
    "chevrolet": "한국지엠",
    "gm": "한국지엠",
    "ssangyong": "쌍용",
    "renault": "르노코리아",
    "volkswagen": "폭스바겐그룹",
}

# DB에서 데이터 로드
@st.cache_data(show_spinner=False)
def load_data():
    conn = get_connection()
    query = """
        SELECT 
            brand, 
            name, 
            release_start AS start_date,
            release_end AS end_date,
            recall_type,
            announcement_start AS notice_date,
            announcement_end AS fix_end_date,
            source AS authority,
            defect_description AS reason
        FROM recalls
    """
    df = pd.read_sql(query, con=conn)
    


    # 잘못 들어간 컬럼명 행 제거 (자동 정제)
    df = df[df["brand"].str.lower() != "brand"]
    return df

# 메인 함수 정의
def show():
    st.title("⚠️ 결함 정보 및 리콜 통계")

    df = load_data()
 
    # 문자열 정규화 (str.lower, trim, space remove)
    df["brand_clean"] = df["brand"].astype(str).str.strip().str.replace(r"\s+", "", regex=True).str.lower()
    df["name_clean"] = df["name"].astype(str).str.strip().str.replace(r"\s+", "", regex=True).str.lower()

    # 검색어 입력
    search_input = st.text_input("🔍 브랜드 또는 차종 입력", placeholder="기아, 현대, BMW 등")\
        .strip().lower().replace(" ", "")

    # 검색어가 있을 때만 아래 실행
    if search_input:
        # 매핑된 브랜드 이름으로 변환 후 정규화
        mapped_input = BRAND_MAPPING.get(search_input, search_input)
        mapped_input_clean = mapped_input.strip().lower().replace(" ", "")

        # 검색어 통해 brand/name에 포함되는 데이터 목록 보이기
        matches = df[
            df["brand_clean"].str.contains(mapped_input_clean, na=False) |
            df["name_clean"].str.contains(mapped_input_clean, na=False)
        ]

        # 리스트업 표시 (autocomplete)
        unique_matches = pd.concat([
            matches["brand"], matches["name"]
        ]).dropna().unique().tolist()

        selected_option = None
        if unique_matches:
            selected_option = st.selectbox("🔎 추천 항목을 선택해주세요", ["(선택 안 함)"] + unique_matches)
            if selected_option == "(선택 안 함)":
                selected_option = None

        final_query = selected_option.strip().lower().replace(" ", "") if selected_option else mapped_input_clean

        filtered = df[
            df["brand_clean"].str.contains(final_query, na=False, regex=False) |
            df["name_clean"].str.contains(final_query, na=False, regex=False)
        ]

        if not filtered.empty:
            st.success(f"🔎 '{final_query}'에 대한 리콜 정보 {len(filtered)}개를 찾았습니다.")
            st.dataframe(filtered["brand name recall_type reason".split()])

            # 차량명 기준 리콜 건수 시각화
            st.subheader("📊 검색 결과 내 차량별 리콜 수")
            st.caption("📌 차종별 리콜 수 그래프는 상위 15개만 표시됩니다.")

            name_counts = filtered["name"].value_counts().head(15)
            names = name_counts.index.tolist()
            names = [name[:20] for name in names]
            counts = name_counts.values
            y_pos = np.arange(len(names))

            bar_height = 0.5  # 막대 두께 고정
            margin = 0.5      # 위아래 여백
            num_bars = len(names)
            fig_height = bar_height * num_bars + margin

            fig, ax = plt.subplots(figsize=(10, fig_height))
            ax.barh(y_pos, counts, height=bar_height, color='#F4A261')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(names)
            ax.set_xlabel("리콜 건수")
            # ax.set_ylabel("차량 이름")
            ax.tick_params(labelsize=9)
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))  # x축 정수 눈금
            ax.invert_yaxis()
            st.pyplot(fig)
        else:
            st.warning(f"'{final_query}'에 대한 리콜 정보가 없습니다.")
    
    else:


        st.subheader("🥧 브랜드별 리콜 차량 수 비율 (상위 15개 + 기타)")

        # 전체 브랜드별 리콜 차량 수 (차종 기준)
        brand_total = df.groupby("brand")["name"].nunique().sort_values(ascending=False)

        # 상위 15개 + 기타 합산
        top15 = brand_total.head(15)
        others = brand_total.iloc[15:].sum()

        pie_data = top15.copy()
        if others > 0:
            pie_data["기타"] = others

        # Plotly 도넛형 파이차트 생성
        fig = go.Figure(data=[go.Pie(
            labels=pie_data.index,
            values=pie_data.values,
            hole=0.4,  # 도넛형
            textinfo='percent+label',  # 퍼센트와 라벨 둘 다 표시
            insidetextorientation='horizontal', # 텍스트 가로고정
            textfont=dict(size=16),     # 라벨 기본 폰트
            insidetextfont=dict(size=15),  # 내부 텍스트 폰트
            pull=[0.03]*len(pie_data),  # 살짝 분리 효과(optional)
        )])


        fig.update_layout(
            width=900,
            height=900,
            margin=dict(l=50, r=150, t=50, b=50),
            legend=dict(
                title="브랜드",
                orientation="h",   # 수직 배치
                yanchor="middle",
                y=-0.5,            # 도넛 차트 아래에 배치
                x=0.5,
                xanchor="center",
                font=dict(size=13),
                title_font=dict(size=14)
            )
        )

        # Streamlit에 출력
        st.plotly_chart(fig, use_container_width=True)
        # 전체 브랜드-차종 목록
        st.subheader("📋 전체 브랜드-차종 목록")
        df_display = df[["brand", "name"]].drop_duplicates().sort_values(by="brand").reset_index(drop=True)
        df_display.index = df_display.index + 1  # 인덱스를 1부터 시작
        st.dataframe(df_display)
