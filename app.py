import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- 🌟 설정 🌟 ---
ADMIN_PASSWORD = "0129"
# 공유 설정에서 '편집자'로 되어 있는지 꼭 확인하세요!
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/14jEW_hjXXROFQ8ncrSJ35LBH_rlTiAVjq3AMnqbCXEE/edit?usp=sharing"
OPTIONS = ["매우 만족", "만족", "보통", "불만", "매우 불만"]

st.set_page_config(page_title="만포대체력단련장 설문조사", layout="centered")

# 구글 시트 연결 함수 (가장 에러 없는 방식)
def get_google_sheet():
    # Streamlit Secrets에서 정보를 가져옴
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # 퍼블릭 시트 접근을 위한 설정
    gc = gspread.public(GOOGLE_SHEET_URL)
    return gc

def create_question(label, key):
    choice = st.radio(label, OPTIONS, horizontal=True, key=key)
    reason = ""
    if choice in ["불만", "매우 불만"]:
        reason = st.text_input(f"'{label}'에 대한 불만 사유를 적어주세요.", key=f"{key}_reason")
    return choice, reason

is_admin = st.query_params.get("admin") == "true"

# 설문 화면
if not is_admin:
    st.title("⛳ 만포대체력단련장 이용 만족도 조사")
    st.write("고객님의 소중한 의견을 듣고 이를 수렴하고자 하오니 많은 참여 부탁드립니다.")

    name = st.text_input("이름을 입력해주세요.")
    phone = st.text_input("전화번호를 입력해주세요. (예: 010-1234-5678)")
    
    st.markdown("---")
    st.subheader("2. 만족도 평가")
    q1, r1 = create_question("1. 직원 서비스", "q1")
    q2, r2 = create_question("2. 식당", "q2")
    q3, r3 = create_question("3. 락카", "q3")
    q4, r4 = create_question("4. 코스", "q4")
    q5, r5 = create_question("5. 경기진행 및 캐디", "q5")

    if st.button("설문 제출하기", type="primary"):
        if not name or not phone:
            st.warning("이름과 전화번호를 모두 입력해주세요!")
        else:
            # 시트에 바로 한 줄 추가하는 방식
            try:
                # 스트림릿의 기본 연결 방식 사용
                from streamlit_gsheets import GSheetsConnection
                conn = st.connection("gsheets", type=GSheetsConnection)
                
                # 기존 데이터 가져오기
                existing_data = conn.read(spreadsheet=GOOGLE_SHEET_URL)
                
                new_row = pd.DataFrame([{
                    "날짜": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "이름": name, "전화번호": phone,
                    "직원서비스": q1, "직원_사유": r1,
                    "식당": q2, "식당_사유": r2,
                    "락카": q3, "락카_사유": r3,
                    "코스": q4, "코스_사유": r4,
                    "경기진행": q5, "경기_사유": r5
                }])
                
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(spreadsheet=GOOGLE_SHEET_URL, data=updated_df)
                st.success("설문이 제출되었습니다. 감사합니다!")
                st.balloons()
            except Exception as e:
                st.error(f"저장 중 오류가 발생했습니다. 구글 시트 공유 설정을 '편집자'로 바꿨는지 확인해주세요!")

# 관리자 화면
else:
    st.title("🔒 관리자 전용 페이지")
    # (관리자 코드는 이전과 동일하므로 생략하거나 그대로 유지하세요)
    # ... 이전 코드와 동일 ...
