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

import streamlit as st

st.set_page_config(page_title="팀플방 시간표 겹침 추천", layout="centered")

# 1. 팀플방 생성
st.header("👥 팀플 방 생성")

if 'rooms' not in st.session_state:
    st.session_state['rooms'] = []

room_name = st.text_input("팀플방 이름 입력")
if st.button("방 생성"):
    st.session_state['rooms'].append({'name': room_name, 'members': []})
    st.success(f"'{room_name}' 팀플방이 생성되었습니다.")

st.divider()

# 2. 팀원별 시간표 업로드 및 가능 시간 선택
st.header("🙋‍♂️ 팀원 정보 입력 및 시간표 업로드")

selected_room = st.selectbox(
    "팀플방 선택", [r['name'] for r in st.session_state['rooms']] if st.session_state['rooms'] else [])

if selected_room:
    room_idx = [r['name'] for r in st.session_state['rooms']].index(selected_room)
    member_name = st.text_input("팀원 이름", key="mem_name")
    timetable_img = st.file_uploader("시간표 이미지(jpg, png)", type=["jpg", "jpeg", "png"])
    
    # 선택할 수 있는 시간대 예시 (직접 수정 가능)
    time_slots = ["월 10-12", "월 12-14", "화 10-12", "수 14-16", "목 16-18", "금 14-16"]
    possible_times = st.multiselect("내가 가능한 시간대 선택(중복 가능)", time_slots, key="possible_times")
    
    if st.button("팀원 추가"):
        st.session_state['rooms'][room_idx]['members'].append({
            'name': member_name,
            'timetable_img': timetable_img,
            'times': possible_times
        })
        st.success(f"{member_name}님이 팀플방 '{selected_room}'에 추가되었습니다.")
    
    st.subheader("팀원 리스트")
    for mem in st.session_state['rooms'][room_idx]['members']:
        st.write(f"이름: {mem['name']}, 가능한 시간: {mem['times']}")
        if mem['timetable_img']:
            st.image(mem['timetable_img'], width=250, caption=f"{mem['name']} 시간표")

st.divider()

# 3. 겹치는 시간 자동 추천
st.header("⏰ 팀플 가능 시간 자동 추천")

if selected_room and st.session_state['rooms'][room_idx]['members']:
    all_times = [set(mem['times']) for mem in st.session_state['rooms'][room_idx]['members'] if mem['times']]
    if all_times:
        # 모든 팀원의 가능 시간의 교집합 구하기
        common_times = set.intersection(*all_times) if len(all_times) > 1 else all_times[0]
        if common_times:
            st.success(f"모든 팀원이 가능한 시간대: {', '.join(common_times)}")
        else:
            st.warning("모든 팀원이 가능한 시간대가 없습니다. (시간 선택을 다시 확인!)")
    else:
        st.info("모든 팀원이 가능한 시간을 선택해야 추천이 가능합니다.")
else:
    st.info("팀플방을 만들고, 팀원을 추가해주세요.")

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.header("📝 과제 리스트 & 마감 알림")

# 과제 리스트 예시
if 'tasks' not in st.session_state:
    st.session_state['tasks'] = []

task = st.text_input("과제/할 일 입력", key='task_input')
deadline = st.date_input("마감기한 선택", min_value=datetime.now().date(), key='task_deadline')
if st.button("과제 추가"):
    st.session_state['tasks'].append({'task': task, 'deadline': deadline, 'done': False})

# 알림 체크(마감 1일 전~당일 알림)
now = datetime.now().date()
for t in st.session_state['tasks']:
    if not t['done'] and t['deadline'] - now <= timedelta(days=1):
        st.warning(f"[알림] '{t['task']}' 마감이 임박했습니다! (마감: {t['deadline']})")

# 리스트 표시
for i, t in enumerate(st.session_state['tasks']):
    col1, col2 = st.columns([5,2])
    with col1:
        st.write(f"{t['task']} (마감: {t['deadline']})")
    with col2:
        if st.checkbox("완료", value=t['done'], key=f'done_{i}'):
            st.session_state['tasks'][i]['done'] = True

import streamlit as st

st.header("📍 팀플 근처 장소 추천 (네이버 지도)")

# 지도 보여줄 위치(예: 가천대학교)
lat, lng = 37.45161, 127.12754   # 가천대 위도/경도 예시

naver_map_iframe = f"""
<iframe
  src="https://map.naver.com/p/search/{lat},{lng}"
  width="100%"
  height="400"
  frameborder="0"
  style="border:0;"
  allowfullscreen
></iframe>
"""

st.markdown(naver_map_iframe, unsafe_allow_html=True)

st.info("지도에서 직접 장소를 검색하거나, 주변 장소(카페/스터디룸 등)를 클릭해볼 수 있습니다.")
