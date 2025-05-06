import streamlit as st
import pandas as pd

st.title("연결정산표 프로토타입 시스템")

st.header("Step 1: 데이터 업로드 및 구분 지정")

uploaded_data = []

upload_count = st.number_input("업로드할 파일 개수 선택", min_value=1, max_value=10, value=3)

for i in range(upload_count):
    st.subheader(f"파일 {i+1}")
    file = st.file_uploader(f"파일 {i+1} 업로드", type=["csv"], key=f"file_{i}")
    file_type = st.selectbox(
        f"이 파일의 구분을 선택하세요 (파일 {i+1})",
        ("모회사별도 (A1)", "자회사1별도 (A2)", "자회사2별도 (A3)", "연결조정 (B1)", "내부거래제거 (B2)"),
        key=f"type_{i}"
    )
    
    if file is not None:
        df = pd.read_csv(file)
        st.write("업로드된 데이터")
        st.dataframe(df)
        uploaded_data.append({"type": file_type, "data": df})

# 데이터 분리
data_dict = {
    "A1": pd.DataFrame(columns=["표준계정과목코드", "표준계정과목명", "금액"]),
    "A2": pd.DataFrame(columns=["표준계정과목코드", "표준계정과목명", "금액"]),
    "A3": pd.DataFrame(columns=["표준계정과목코드", "표준계정과목명", "금액"]),
    "B1": pd.DataFrame(columns=["표준계정과목코드", "표준계정과목명", "금액"]),
    "B2": pd.DataFrame(columns=["표준계정과목코드", "표준계정과목명", "금액"]),
}

for item in uploaded_data:
    type_key = ""
    if "A1" in item["type"]:
        type_key = "A1"
    elif "A2" in item["type"]:
        type_key = "A2"
    elif "A3" in item["type"]:
        type_key = "A3"
    elif "B1" in item["type"]:
        type_key = "B1"
    elif "B2" in item["type"]:
        type_key = "B2"
    
    df = item["data"]
    required_cols = ["표준계정과목코드", "표준계정과목명", "금액"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"{type_key} 데이터에 필수 컬럼 {missing_cols} 이 없습니다. 빈 데이터로 처리합니다.")
        continue

    data_dict[type_key] = df

# 연결정산표 생성
st.header("Step 2: 연결정산표")

# 표준계정 목록 확보
concat_list = []
for key in data_dict:
    df = data_dict[key]
    if "표준계정과목코드" in df.columns and "표준계정과목명" in df.columns:
        concat_list.append(df[["표준계정과목코드", "표준계정과목명"]])

if concat_list:
    codes = pd.concat(concat_list).drop_duplicates()
else:
    codes = pd.DataFrame(columns=["표준계정과목코드", "표준계정과목명"])

# 데이터 병합
for key in ["A1", "A2", "A3", "B1", "B2"]:
    codes = pd.merge(codes, data_dict[key][["표준계정과목코드", "금액"]].rename(columns={"금액": key}),
                     on="표준계정과목코드", how="left")

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
