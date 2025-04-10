import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from sqlalchemy import create_engine
import pymysql
from utils.db import get_connection  # DB 연결 함수 가져오기
from matplotlib.ticker import MaxNLocator
import io


# 한국어 폰트 설정
matplotlib.rc('font', family='Malgun Gothic')
matplotlib.rcParams['axes.unicode_minus'] = False

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
    st.header("🚗 결함 정보 및 리콜 통계")

    df = load_data()
    
    # 문자열 정규화 (str.lower, trim, space remove)
    df["brand_clean"] = df["brand"].astype(str).str.strip().str.replace(r"\s+", "", regex=True).str.lower()
    df["name_clean"] = df["name"].astype(str).str.strip().str.replace(r"\s+", "", regex=True).str.lower()

    # 검색어 입력
    search_input = st.text_input("🔍 브랜드 또는 차종 입력", placeholder="BMW, 기아, K5 등")\
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
            counts = name_counts.values
            y_pos = np.arange(len(names))

            bar_height = 0.5  # 막대 두께 고정
            margin = 0.5      # 위아래 여백
            num_bars = len(names)
            fig_height = bar_height * num_bars + margin

            fig, ax = plt.subplots(figsize=(10, fig_height))
            ax.barh(y_pos, counts, height=bar_height)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(names)
            ax.set_xlabel("리콜 건수")
            ax.set_ylabel("차량 이름")
            ax.tick_params(labelsize=9)
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))  # x축 정수 눈금
            ax.invert_yaxis()
            st.pyplot(fig)
        else:
            st.warning(f"'{final_query}'에 대한 리콜 정보가 없습니다.")
    
    else:
        # 검색어 없을 때: 도넛형 파이차트 표시
        st.subheader("🥧 브랜드별 리콜 차량 수 비율 (상위 15개 + 기타)")
    
        # 전체 브랜드별 리콜 차량 수 (차종 기준)
        brand_total = df.groupby("brand")["name"].nunique().sort_values(ascending=False)

        # 상위 15개 + 기타 합산
        top15 = brand_total.head(15)
        others = brand_total.iloc[15:].sum()

        pie_data = top15.copy()
        if others > 0:
            pie_data["기타"] = others

        # 파이차트 그리기 (도넛형 + 라벨 안 겹치게)
        fig, ax = plt.subplots(figsize=(5, 5))
        wedges, texts, autotexts = ax.pie(
            pie_data.values,
            autopct='%1.1f%%',
            startangle=140,
            counterclock=False,
            textprops={'fontsize': 9},
            wedgeprops=dict(width=0.7)  # 도넛 스타일
        )
        ax.axis("equal")

        for autotext in autotexts:
            autotext.set_position((autotext.get_position()[0] * 1.3,  # x를 1.4배 멀리
                                   autotext.get_position()[1] * 1.3)) # y를 1.4배 멀리
        
        # 오른쪽에 범례로 브랜드명 정리
        ax.legend(
            wedges,
            pie_data.index,
            title="브랜드",
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            fontsize=9,
            title_fontsize=10
        )

        # 메모리에 이미지 저장 후 Streamlit에 출력
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight", transparent=True)
        buf.seek(0)
        st.image(buf, width=750)  # 화면에 적당한 크기로 표시

        # 전체 브랜드-차종 목록
        st.subheader("📋 전체 브랜드-차종 목록")
        st.dataframe(df[["brand", "name"]].drop_duplicates().sort_values(by="brand"))