import streamlit as st
import pandas as pd

st.title("연결정산표 프로토타입 시스템")

# 업로드 파일 받기
st.header("Step 1: 회사별 별도 데이터 업로드 (A1, A2, A3)")

uploaded_files = st.file_uploader("별도 재무제표 업로드 (모회사 A1, 자회사1 A2, 자회사2 A3)", type=["csv"], accept_multiple_files=True)

dataframes = {}
for i, file in enumerate(uploaded_files):
    if file is not None:
        df = pd.read_csv(file)
        st.write(f"업로드된 데이터 (A{i+1})")
        st.dataframe(df)
        dataframes[f"A{i+1}"] = df

# 연결조정 데이터 업로드
st.header("Step 2: 연결조정 데이터 업로드 (B1, B2)")
uploaded_adjust = st.file_uploader("연결조정 데이터 업로드 (B1, B2)", type=["csv"])

adjust_df = None
if uploaded_adjust is not None:
    adjust_df = pd.read_csv(uploaded_adjust)
    st.write("업로드된 연결조정 데이터")
    st.dataframe(adjust_df)

# 계산 시작
if len(dataframes) == 3 and adjust_df is not None:
    st.header("Step 3: 연결정산표 계산 결과")

    # 표준계정 기준으로 별도 합산
    merged_df = pd.DataFrame()
    for key, df in dataframes.items():
        if merged_df.empty:
            merged_df = df.copy()
            merged_df.rename(columns={"금액": f"{key}"}, inplace=True)
        else:
            merged_df = pd.merge(merged_df, df, on=["표준계정과목코드", "표준계정과목명"], how='outer', suffixes=("", f"_{key}"))
            merged_df.rename(columns={"금액": f"{key}"}, inplace=True)

    merged_df = merged_df.fillna(0)
    merged_df["별도단순합산"] = merged_df["A1"] + merged_df["A2"] + merged_df["A3"]

    # 연결조정 데이터 병합
    merged_df = pd.merge(merged_df, adjust_df, on=["표준계정과목코드", "표준계정과목명"], how='left')
    merged_df = merged_df.fillna(0)
    merged_df.rename(columns={"B1": "연결조정합산(B1)", "B2": "내부거래제거(B2)"}, inplace=True)

    # 최종 연결후금액 계산
    merged_df["연결후금액"] = merged_df["별도단순합산"] + merged_df["연결조정합산(B1)"] + merged_df["내부거래제거(B2)"]

    # 컬럼 순서 재정렬
    ordered_columns = ["표준계정과목코드", "표준계정과목명", "연결후금액", "내부거래제거(B2)", "연결조정합산(B1)", "별도단순합산", "A1", "A2", "A3"]
    merged_df = merged_df[ordered_columns]

    # 결과 출력
    st.subheader("📊 최종 연결정산표")
    st.dataframe(merged_df)

    # 다운로드 기능
    csv = merged_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="연결정산표 다운로드 (CSV)",
        data=csv,
        file_name='연결정산표.csv',
        mime='text/csv',
    )
