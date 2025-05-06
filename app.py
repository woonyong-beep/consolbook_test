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

    # 표준계정 후보 리스트
    표준계정_리스트 = ["매출", "매입", "현금", "비용", "기타"]

    # 표준계정 컬럼 생성
    df['표준계정'] = ""

    # 데이터 행별로 selectbox 제공 (key 중복 방지 위해 index 사용)
    for idx, row in df.iterrows():
        표준계정 = st.selectbox(
            f"[{idx}] '{row['계정과목']}' → 표준계정 선택",
            표준계정_리스트,
            key=f"map_{idx}"
        )
        df.loc[idx, '표준계정'] = 표준계정

    st.write("계정 매핑 결과:")
    st.dataframe(df)

    # 연결조정내역 기록
    st.write("연결조정내역 기록 (조정사유 입력)")

    # 조정사유 컬럼 생성
    df['조정사유'] = ""

    # 데이터 행별로 text_input 제공 (index 기반 key 사용)
    for idx, row in df.iterrows():
        조정사유 = st.text_input(
            f"[{idx}] '{row['표준계정']}' → 조정사유 입력",
            key=f"adj_{idx}"
        )
        df.loc[idx, '조정사유'] = 조정사유

    st.write("조정내역 포함 데이터:")
    st.dataframe(df)

    # 연결 재무제표 합산
    st.write("연결 재무제표 (표준계정 기준 합산):")

    연결 = df.groupby('표준계정')['금액'].sum().reset_index()
    st.dataframe(연결)

    # 엑셀로 내보내기 (CSV 다운로드)
    st.write("엑셀 파일로 내보내기:")

    # CSV 변환 함수 (캐시 사용)
    @st.cache_data
    def convert_df_to_csv(dataframe):
        return dataframe.to_csv(index=False).encode('utf-8-sig')

    csv = convert_df_to_csv(df)

    st.download_button(
        label="연결조정내역 포함 데이터 다운로드 (CSV)",
        data=csv,
        file_name='연결조정내역.csv',
        mime='text/csv',
    )
