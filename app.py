import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 🌟 설정: 관리자 비밀번호 🌟 ---
ADMIN_PASSWORD = "0129"
DATA_FILE = "survey_results.csv"
OPTIONS = ["매우 만족", "만족", "보통", "불만", "매우 불만"]

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        columns = ["날짜", "이름", "전화번호", "직원서비스", "직원_사유", "식당", "식당_사유", "락카", "락카_사유", "코스", "코스_사유", "경기진행", "경기_사유"]
        return pd.DataFrame(columns=columns)

def create_question(label, key):
    choice = st.radio(label, OPTIONS, horizontal=True, key=key)
    reason = ""
    if choice in ["불만", "매우 불만"]:
        reason = st.text_input(f"'{label}'에 대한 불만 사유를 적어주세요.", key=f"{key}_reason")
    return choice, reason

st.set_page_config(page_title="만포대체력단련장 설문조사", layout="centered")

is_admin = st.query_params.get("admin") == "true"

# ==========================================================
# 📝 [일반 사용자] 설문 참여 화면
# ==========================================================
if not is_admin:
    st.title("⛳ 만포대체력단련장 이용 만족도 조사")
    st.write("고객님의 소중한 의견을 듣고 이를 수렴하고자 하오니 많은 참여 부탁드립니다.")

    today = datetime.now()
    weekdays = ['월', '화', '수', '목', '금', '토', '일']
    today_str = today.strftime(f"%Y년 %m월 %d일 ({weekdays[today.weekday()]})")
    
    st.info(f"📅 **오늘의 설문 일자 : {today_str}**")

    st.subheader("1. 기본 정보")
    name = st.text_input("이름을 입력해주세요.")
    phone = st.text_input("전화번호를 입력해주세요. (예: 010-1234-5678)")
    
    st.markdown("---")
    st.subheader("2. 만족도 평가")
    
    q1, r1 = create_question("1. 직원 서비스", "q1")
    q2, r2 = create_question("2. 식당", "q2")
    q3, r3 = create_question("3. 락카", "q3")
    q4, r4 = create_question("4. 코스", "q4")
    q5, r5 = create_question("5. 경기진행 및 캐디", "q5")

    st.markdown("---")
    if st.button("설문 제출하기", type="primary"):
        if not name or not phone:
            st.warning("이름과 전화번호를 모두 입력해주세요!")
        else:
            new_data = {
                "날짜": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "이름": name, "전화번호": phone,
                "직원서비스": q1, "직원_사유": r1,
                "식당": q2, "식당_사유": r2,
                "락카": q3, "락카_사유": r3,
                "코스": q4, "코스_사유": r4,
                "경기진행": q5, "경기_사유": r5
            }
            df = load_data()
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
            st.success("설문이 성공적으로 제출되었습니다. 감사합니다!")

# ==========================================================
# 📊 [관리자] 결과 보기 화면
# ==========================================================
else:
    st.title("🔒 관리자 전용 페이지")
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.pwd_error = False

    # --- 🌟 수정된 부분: 비밀번호 확인 함수 생성 ---
    def check_password():
        if st.session_state.pwd_input == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.pwd_error = False
        else:
            st.session_state.pwd_error = True

    if not st.session_state.authenticated:
        # on_change: 입력칸에서 엔터를 치면 check_password 함수 실행
        st.text_input("관리자 비밀번호를 입력하세요:", type="password", key="pwd_input", on_change=check_password)
        
        # on_click: 버튼을 마우스로 누르면 check_password 함수 실행
        st.button("확인", on_click=check_password)
        
        if st.session_state.pwd_error:
            st.error("비밀번호가 틀렸습니다.")
    # --------------------------------------------------------
    else:
        if st.button("로그아웃"):
            st.session_state.authenticated = False
            st.session_state.pwd_error = False
            st.rerun()
            
        st.markdown("---")
        df = load_data()
        
        if df.empty:
            st.info("아직 제출된 설문 결과가 없습니다.")
        else:
            df['날짜(일자)'] = df['날짜'].astype(str).str.split(' ').str[0]
            
            show_all = st.checkbox("모든 날짜의 누적 결과 보기")
            
            if show_all:
                selected_date_str = "전체"
                filtered_df = df
            else:
                selected_date = st.date_input("📅 조회할 날짜를 달력에서 선택하세요:")
                selected_date_str = selected_date.strftime("%Y-%m-%d")
                filtered_df = df[df['날짜(일자)'] == selected_date_str]
                
            st.dataframe(filtered_df.drop(columns=['날짜(일자)']), use_container_width=True)
            
            st.markdown("---")
            if filtered_df.empty:
                st.warning(f"선택하신 날짜({selected_date_str})에는 제출된 설문이 없습니다.")
            else:
                st.write(f"### 📊 '{selected_date_str}' 항목별 만족도 요약")
                questions = ["직원서비스", "식당", "락카", "코스", "경기진행"]
                for q in questions:
                    st.write(f"**{q}**")
                    counts = filtered_df[q].value_counts().reindex(OPTIONS, fill_value=0)
                    st.bar_chart(counts)
                    
                st.markdown("---")
                st.write(f"### 🚨 '{selected_date_str}' 불만/매우 불만 접수 사유")
                for q in questions:
                    reason_col = f"{q[:2]}_사유" if q not in ["직원서비스", "경기진행"] else ("직원_사유" if q == "직원서비스" else "경기_사유")
                    reasons = filtered_df[filtered_df[reason_col] != ""][["날짜", "이름", reason_col]]
                    if not reasons.empty:
                        st.write(f"**{q} 관련 사유**")
                        st.dataframe(reasons, use_container_width=True)