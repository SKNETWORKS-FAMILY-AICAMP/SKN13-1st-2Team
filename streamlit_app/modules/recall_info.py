import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# ✅ 한글 폰트 설정 (Windows용)
matplotlib.rc('font', family='Malgun Gothic')
matplotlib.rcParams['axes.unicode_minus'] = False

def show():
    st.header("🚗 결함 정보 및 리콜 통계")

    # ✅ 데이터 로딩
    df = pd.read_csv("data/recalls.csv",
                     encoding="utf-8",
                     quotechar='"',
                     on_bad_lines='skip',
                     header=None,
                     names=["brand", "name", "start_date", "end_date", "recall_type",
                            "notice_date", "fix_end_date", "authority", "reason"])

    # ✅ 검색창
    st.subheader("🔍 브랜드 또는 차종 입력")
    search_input = st.text_input("브랜드 또는 차량명을 입력하세요 (예: BMW, 아이오닉, 쏘나타 등)")

    # ✅ 추천 리스트 생성
    recommendations = df[
        df["brand"].str.contains(search_input, case=False, na=False) |
        df["name"].str.contains(search_input, case=False, na=False)
    ][["brand", "name"]]

    options = pd.concat([
        recommendations["brand"],
        recommendations["name"]
    ]).dropna().unique().tolist()

    options = [o for o in options if search_input.lower() in o.lower()][:10]

    # ✅ 선택 옵션: 자동선택 방지
    selected_option = None
    if options:
        selected_option = st.selectbox("🔍 추천된 항목 중에서 선택하세요", ["(선택 안 함)"] + options)
        if selected_option == "(선택 안 함)":
            selected_option = None

    # ✅ 최종 검색어: 추천 선택값 > 입력값
    final_search = selected_option if selected_option else search_input
    is_searching = bool(final_search.strip())

    # ✅ 검색 처리
    if is_searching:
        filtered = df[
            df["brand"].str.contains(final_search, case=False, na=False) |
            df["name"].str.contains(final_search, case=False, na=False)
        ]

        if not filtered.empty:
            st.success(f"🔎 '{final_search}'에 대한 리콜 정보 {len(filtered)}건을 찾았습니다.")
            st.dataframe(filtered[["brand", "name", "start_date", "recall_type", "reason"]])

            st.subheader("📊 검색 결과 내 차량별 리콜 수")
            st.caption("📌 차종별 리콜 수 그래프는 상위 15개만 표시됩니다.")

            name_counts = filtered["name"].value_counts().head(15)

            # ✅ 막대 두께 자동 조절
            bar_height = 0.5
            graph_height = max(5, len(name_counts) * bar_height)

            fig2, ax2 = plt.subplots(figsize=(10, graph_height))
            name_counts.plot(kind="barh", ax=ax2)
            ax2.set_xlabel("리콜 건수")
            ax2.set_ylabel("차량 이름")
            ax2.tick_params(labelsize=9)
            ax2.invert_yaxis()
            st.pyplot(fig2)
        else:
            st.warning(f"'{final_search}'에 대한 리콜 정보가 없습니다.")

    # ✅ 검색 중이 아닐 때만 전체 데이터 표시
    if not is_searching:
        st.subheader("📋 브랜드별 차량 목록")
        st.dataframe(df[["brand", "name"]].drop_duplicates().sort_values(by="brand"))

        st.subheader("📊 리콜 차량 수 TOP 10")
        brand_counts = df["brand"].value_counts().head(10)

        fig, ax = plt.subplots(figsize=(10, 6))
        brand_counts.plot(kind="barh", ax=ax)
        ax.set_xlabel("리콜 차량 수")
        ax.set_ylabel("브랜드")
        ax.invert_yaxis()
        st.pyplot(fig)