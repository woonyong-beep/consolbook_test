import streamlit as st
import pandas as pd

st.title("연결정산표 프로토타입 시스템")

# 업로드 파일 받기
st.header("Step 1: 회사별 별도 데이터 업로드 (A1, A2, A3)")

uploaded_files = st.file_uploader("별도 재무제표 업로드 (모회사 A1, 자회사1 A2, 자회사2 A3)", type=["csv"], accept_multiple_files=True)

dataframes = {}
company_labels = ["A1", "A2", "A3"]
required_cols = ["표준계정과목코드", "표준계정과목명", "금액"]

for i, label in enumerate(company_labels):
    if i < len(uploaded_files):
        df = pd.read_csv(uploaded_files[i])

        # 컬럼 체크 (방법1)
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"{label} 파일에 필수 컬럼이 없습니다: {missing_cols}. 빈 데이터로 처리합니다.")
            df = pd.DataFrame(columns=required_cols)

        st.write(f"업로드된 데이터 ({label})")
        st.dataframe(df)

        dataframes[label] = df
    else:
        # 파일이 없으면 빈 데이터로 생성
        dataframes[label] = pd.DataFrame(columns=required_cols)

# 연결조정 데이터 업로드
st.header("Step 2: 연결조정 데이터 업로드 (B1, B2)")
uploaded_adjust = st.file_uploader("연결조정 데이터 업로드 (B1, B2)", type=["csv"])

if uploaded_adjust is not None:
    adjust_df = pd.read_csv(uploaded_adjust)

    # 컬럼 체크
    adjust_required_cols = ["표준계정과목코드", "표준계정과목명", "B1", "B2"]
    missing_cols = [col for col in adjust_required_cols if col not in adjust_df.columns]
    if missing_cols:
        st.error(f"연결조정 파일에 필수 컬럼이 없습니다: {missing_cols}. 빈 데이터로 처리합니다.")
        adjust_df = pd.DataFrame(columns=adjust_required_cols)

    st.write("업로드된 연결조정 데이터")
    st.dataframe(adjust_df)
else:
    adjust_df = pd.DataFrame(columns=["표준계정과목코드", "표준계정과목명", "B1", "B2"])

# 연결정산표 만들기
st.header("Step 3: 연결정산표")

# 표준계정 목록 확보 (방법2 적용 → 유효한 데이터만 합치기)
concat_list = []
for df in list(dataframes.values()) + [adjust_df]:
    if "표준계정과목코드" in df.columns and "표준계정과목명" in df.columns:
        concat_list.append(df[["표준계정과목코드", "표준계정과목명"]])

if concat_list:
    codes = pd.concat(concat_list).drop_duplicates()
else:
    codes = pd.DataFrame(columns=["표준계정과목코드", "표준계정과목명"])

# 회사별 데이터 합치기
for label in company_labels:
    codes = pd.merge(codes, dataframes[label][["표준계정과목코드", "금액"]].rename(columns={"금액": label}), 
                     on="표준계정과목코드", how="left")

# 연결조정 데이터 합치기
codes = pd.merge(codes, adjust_df, on=["표준계정과목코드", "표준계정과목명"], how="left")

# 결측값 0으로
codes = codes.fillna(0)

# 별도단순합산 계산
codes["별도단순합산"] = codes["A1"] + codes["A2"] + codes["A3"]

# 연결후금액 계산
codes["연결후금액"] = codes["별도단순합산"] + codes["B1"] + codes["B2"]

# 컬럼 순서 재정렬
ordered_columns = ["표준계정과목코드", "표준계정과목명", "연결후금액", "B2", "B1", "별도단순합산", "A1", "A2", "A3"]
codes = codes[ordered_columns]

# 결과 출력
st.subheader("📊 최종 연결정산표")
st.dataframe(codes)

# 다운로드
csv = codes.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="연결정산표 다운로드 (CSV)",
    data=csv,
    file_name='연결정산표.csv',
    mime='text/csv',
)
