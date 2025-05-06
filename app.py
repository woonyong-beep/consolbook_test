import streamlit as st
import pandas as pd

st.title("연결 재무제표 프로토타입")

uploaded_file = st.file_uploader("별도재무제표 엑셀 업로드", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write("업로드된 데이터:")
    st.dataframe(df)

    st.write("내부거래 상계 처리 결과:")

    # 내부거래 간단 상계 처리
    df['상계'] = df['금액'] * -1
    상계_df = pd.merge(df, df, left_on='상계', right_on='금액', suffixes=('_좌', '_우'))

    st.dataframe(상계_df)

    st.write("연결 재무제표 (단순 합산):")
    연결 = df.groupby('계정과목')['금액'].sum().reset_index()
    st.dataframe(연결)