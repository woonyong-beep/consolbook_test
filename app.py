import streamlit as st
import pandas as pd

st.title("연결 재무제표 프로토타입")

# 파일 업로드
uploaded_file = st.file_uploader("재무제표 업로드 (엑셀 or CSV)", type=["xlsx", "csv"])

if uploaded_file is not None:
    # 파일 읽기
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("업로드된 데이터:")
    st.dataframe(df)

    # 계정 매핑
    st.write("계정 매핑하기 (표준계정 지정)")

    # 표준계정 후보 리스트 (자유롭게 추가 가능)
    표준계정_리스트 = ["매출", "매입", "현금", "비용", "기타"]

    # 사용자에게 계정 매핑 selectbox로 입력 받기
    df['표준계정'] = df['계정과목'].apply(
        lambda x: st.selectbox(f"'{x}' → 표준계정 선택", 표준계정_리스트, key=f"map_{x}")
    )

    st.write("계정 매핑 결과:")
    st.dataframe(df)

    # 연결조정내역 기록
    st.write("연결조정내역 기록 (조정사유 입력)")

    df['조정사유'] = df['표준계정'].apply(
        lambda x: st.text_input(f"'{x}' → 조정사유 입력", key=f"adj_{x}")
    )

    st.write("조정내역 포함 데이터:")
    st.dataframe(df)

    # 연결 재무제표 합산
    st.write("연결 재무제표 (표준계정 기준 합산):")

    연결 = df.groupby('표준계정')['금액'].sum().reset_index()

    st.dataframe(연결)

    # 엑셀로 내보내기
    st.write("엑셀 파일로 내보내기:")

    # 다운로드용 엑셀파일 생성
    @st.cache_data
    def convert_df_to_excel(df):
        return df.to_csv(index=False).encode('utf-8-sig')

    excel = convert_df_to_excel(df)

    st.download_button(
        label="연결조정내역 포함 데이터 다운로드 (CSV)",
        data=excel,
        file_name='연결조정내역.csv',
        mime='text/csv',
    )
