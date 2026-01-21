import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 페이지 기본 설정
st.set_page_config(page_title="스마트 BMI 계산기", page_icon="⚖️")

# 2. 데이터 저장/불러오기 관련 함수
FILE_NAME = 'bmi_history.csv'

def load_data():
    """저장된 BMI 기록을 불러옵니다."""
    if not os.path.exists(FILE_NAME):
        # 파일이 없으면 빈 데이터프레임 생성
        return pd.DataFrame(columns=["날짜", "키(cm)", "몸무게(kg)", "BMI", "상태"])
    return pd.read_csv(FILE_NAME)

def save_data(ki, muge, bmi, status):
    """새로운 측정 결과를 CSV 파일에 저장합니다."""
    new_data = {
        "날짜": [datetime.now().strftime("%Y-%m-%d %H:%M")],
        "키(cm)": [ki],
        "몸무게(kg)": [muge],
        "BMI": [round(bmi, 2)],
        "상태": [status]
    }
    new_df = pd.DataFrame(new_data)
    
    if not os.path.exists(FILE_NAME):
        new_df.to_csv(FILE_NAME, index=False, encoding='utf-8-sig')
    else:
        # 기존 데이터에 이어서 저장 (header=False)
        new_df.to_csv(FILE_NAME, mode='a', header=False, index=False, encoding='utf-8-sig')

# 3. BMI 계산 로직 함수
def BMI_calc(ki, muge):
    return muge / (ki * ki)

def get_bmi_status(result):
    if result >= 35:
        return "3단계 고도비만", "error"
    elif 30 <= result < 35:
        return "2단계 비만", "error"
    elif 25 <= result < 30:
        return "1단계 비만", "warning"
    elif 23 <= result < 25:
        return "과체중", "warning"
    elif 18.5 <= result < 23:
        return "정상", "success"
    else:
        return "저체중", "info"

# --- 메인 UI 시작 ---

st.title("⚖️ 스마트 BMI 계산기")
st.write("키와 몸무게를 입력하고 기록을 저장하여 변화를 관리하세요.")
st.divider()

# 입력 받기
col1, col2 = st.columns(2)
with col1:
    ki_input = st.number_input("키를 입력하세요 (cm)", min_value=0.0, step=0.1, format="%.1f")
with col2:
    muge_input = st.number_input("몸무게를 입력하세요 (kg)", min_value=0.0, step=0.1, format="%.1f")

# 계산 및 저장 버튼
if st.button("BMI 계산 및 저장"):
    if ki_input > 0 and muge_input > 0:
        # 계산
        result = BMI_calc((ki_input / 100), muge_input)
        status_text, status_color = get_bmi_status(result)
        
        # 결과 표시
        st.subheader(f"당신의 BMI 지수는 **{result:.2f}** 입니다.")
        
        if status_color == 'error':
            st.error(f"🚨 {status_text}입니다.")
        elif status_color == 'warning':
            st.warning(f"⚠️ {status_text}입니다.")
        elif status_color == 'success':
            st.success(f"✅ {status_text}입니다.")
        else:
            st.info(f"ℹ️ {status_text}입니다.")

        # 데이터 저장 실행
        save_data(ki_input, muge_input, result, status_text)
        st.toast("측정 결과가 저장되었습니다!", icon="💾") # 저장 알림 메시지
            
    else:
        st.warning("키와 몸무게를 정확히 입력해주세요.")

# --- 기록 보기 섹션 ---
st.divider()
st.header("📈 나의 BMI 기록")

# 저장된 데이터 불러오기
df = load_data()

if not df.empty:
    # 탭으로 나누어 보여주기 (표 / 그래프)
    tab1, tab2 = st.tabs(["📋 데이터 목록", "📊 변화 그래프"])
    
    with tab1:
        # 최신순으로 정렬하여 보여주기
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
        
        # 기록 삭제 버튼 (선택 사항)
        if st.button("기록 초기화"):
            if os.path.exists(FILE_NAME):
                os.remove(FILE_NAME)
                st.rerun() # 화면 새로고침
    
    with tab2:
        # 그래프 그리기 (X축: 날짜, Y축: BMI)
        st.line_chart(df, x="날짜", y="BMI")
else:
    st.info("아직 저장된 기록이 없습니다. 위에서 계산을 실행해보세요.")