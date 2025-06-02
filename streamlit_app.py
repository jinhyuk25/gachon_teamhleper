import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="가천대 팀플&과제 앱 프로토타입", layout="centered")

# 1. 과제/To-Do 관리
st.header("📚 과제 관리 (To-Do)")

if 'tasks' not in st.session_state:
    st.session_state['tasks'] = []

task = st.text_input("과제/할 일 입력", key='task_input')
deadline = st.date_input("마감기한 선택", min_value=datetime.now().date())

if st.button("과제 추가"):
    st.session_state['tasks'].append({'task': task, 'deadline': deadline, 'done': False})

# 완료 체크
for i, t in enumerate(st.session_state['tasks']):
    col1, col2, col3 = st.columns([5, 2, 2])
    with col1:
        st.write(f"{t['task']} (마감: {t['deadline']})")
    with col2:
        if st.checkbox("완료", value=t['done'], key=f'done_{i}'):
            st.session_state['tasks'][i]['done'] = True
    with col3:
        if st.button("삭제", key=f'del_{i}'):
            st.session_state['tasks'].pop(i)
            st.experimental_rerun()

st.divider()

# 2. 팀플 방 생성 및 역할분담
st.header("👥 팀플 방 생성/참여")

if 'rooms' not in st.session_state:
    st.session_state['rooms'] = []

if st.button("새 팀플 방 만들기"):
    st.session_state['rooms'].append({'name': f"Team {len(st.session_state['rooms'])+1}",
                                      'members': [], 'roles': {}, 'times': []})

for idx, room in enumerate(st.session_state['rooms']):
    with st.expander(f"팀플 방: {room['name']}"):
        name = st.text_input("이름 입력", key=f'name_{idx}')
        role = st.selectbox("맡은 역할", ["조장", "PPT 담당", "발표 담당", "자료 조사", "기타"], key=f'role_{idx}')
        st.write("시간 가능 여부")
        available_time = st.time_input("가능한 시간(시작)", key=f'time_{idx}_start')
        available_time_end = st.time_input("가능한 시간(끝)", key=f'time_{idx}_end')
        if st.button("참여하기", key=f'join_{idx}'):
            room['members'].append(name)
            room['roles'][name] = role
            room['times'].append((available_time, available_time_end))
            st.success(f"{name}님 팀 참여 완료!")
        st.write("팀원:", room['members'])
        st.write("역할 분담:", room['roles'])
        st.write("팀원별 가능한 시간:", room['times'])

st.divider()

# 3. 만날 수 있는 시간 추천 (가장 겹치는 시간 찾기, 단순 예시)
st.header("⏰ 팀플 만날 수 있는 시간 추천 (예시)")

if st.session_state['rooms']:
    room_sel = st.selectbox("팀 선택", range(len(st.session_state['rooms'])), format_func=lambda x: st.session_state['rooms'][x]['name'])
    room = st.session_state['rooms'][room_sel]
    if room['times']:
        # 단순화: 모두의 시작시간 중 가장 늦은 시간 ~ 모두의 끝시간 중 가장 이른 시간
        start_times = [t[0] for t in room['times']]
        end_times = [t[1] for t in room['times']]
        meet_start = max(start_times)
        meet_end = min(end_times)
        if meet_start < meet_end:
            st.info(f"모든 팀원이 가능한 시간: {meet_start} ~ {meet_end}")
        else:
            st.warning("겹치는 시간이 없습니다. 시간을 조정해주세요.")

st.divider()

# 4. 학교 주변 팀플 장소 추천(예시)
st.header("📍 학교 주변 팀플 장소 추천")

place_list = ["가천대 도서관 그룹스터디룸", "정문 근처 스타벅스", "후문 더벤티", "IT융합대학 세미나실"]
chosen = st.multiselect("장소 선택(여러 개)", place_list)
if chosen:
    st.write("선택한 장소: ", ", ".join(chosen))
    # 평가 시스템(간단)
    rating = st.slider("장소 평점", 1, 5, 3)
    st.write("내 평점: ", rating)

st.success("이게 파이썬 Streamlit으로 만든 간단 프로토타입 예시야. (커스터마이즈, 데이터 연동 등도 확장 가능!)")
