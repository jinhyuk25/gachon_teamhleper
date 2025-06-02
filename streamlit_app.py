import streamlit as st
import random
import string
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="가천대 팀플/과제 도우미", layout="centered")

# ----------------------------------
# 1. 과제 리스트 & 마감 알림
# ----------------------------------
st.title("가천대 팀플 & 과제 도우미")
st.header("📝 과제 리스트 & 마감 알림")

if 'tasks' not in st.session_state:
    st.session_state['tasks'] = []

with st.form("task_form"):
    task = st.text_input("과제/할 일 입력")
    deadline = st.date_input("마감기한 선택", min_value=datetime.now().date())
    submitted = st.form_submit_button("과제 추가")
    if submitted and task:
        st.session_state['tasks'].append({'task': task, 'deadline': deadline, 'done': False})
        st.success(f"'{task}' 과제가 추가되었습니다.")

now = datetime.now().date()
for t in st.session_state['tasks']:
    if not t['done'] and t['deadline'] - now <= timedelta(days=1):
        st.warning(f"[알림] '{t['task']}' 마감이 임박했습니다! (마감: {t['deadline']})")

for i, t in enumerate(st.session_state['tasks']):
    col1, col2 = st.columns([5,2])
    with col1:
        st.write(f"{t['task']} (마감: {t['deadline']})")
    with col2:
        if st.checkbox("완료", value=t['done'], key=f'done_{i}'):
            st.session_state['tasks'][i]['done'] = True

st.divider()

# ----------------------------------
# 2. 내 정보(팀원별) 등록 (사이드바)
# ----------------------------------
st.sidebar.header("내 정보(팀원별) 등록")
user_name = st.sidebar.text_input("이름(닉네임)")
uploaded_img = st.sidebar.file_uploader("내 시간표 이미지", type=["jpg", "png", "jpeg"])
slots = ["월10-12", "월12-14", "화10-12", "수14-16", "목16-18", "금14-16"]
user_times = st.sidebar.multiselect("내가 가능한 시간", slots)
user_save = st.sidebar.button("내 정보 저장")

if 'my_profile' not in st.session_state:
    st.session_state['my_profile'] = None

if user_save and user_name:
    st.session_state['my_profile'] = {
        "name": user_name,
        "img": uploaded_img,
        "times": user_times
    }
    st.sidebar.success("내 정보가 저장되었습니다.")

# ----------------------------------
# 3. 팀플방 생성/입장(팀코드/QR) + 채팅방 + 시간 자동 추천
# ----------------------------------
st.header("👥 팀플방 생성/입장(코드/QR) 및 시간 논의")

if 'team_rooms' not in st.session_state:
    st.session_state['team_rooms'] = {}

# 코드 생성 함수
def generate_team_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

team_code = st.text_input("팀코드 입력(팀원은 팀장에게 코드/QR받아서 입력)", key="team_code_input")
create_room = st.button("팀플방 생성(팀장용)")

if create_room:
    code = generate_team_code()
    st.session_state['current_team_code'] = code
    st.session_state['team_rooms'][code] = {
        "members": [],
        "chats": [],
        "created_at": datetime.now()
    }
    st.success(f"팀플방 코드: {code}")

    # QR코드 생성
    img = qrcode.make(code)
    buf = BytesIO()
    img.save(buf)
    st.image(buf.getvalue(), caption="QR코드로 팀원에게 공유하세요!")

if not team_code and 'current_team_code' in st.session_state:
    team_code = st.session_state['current_team_code']

if team_code:
    st.success(f"팀코드로 팀플방 입장: {team_code}")
    if team_code not in st.session_state['team_rooms']:
        st.session_state['team_rooms'][team_code] = {
            "members": [],
            "chats": [],
            "created_at": datetime.now()
        }
    # 팀원정보 등록
    if st.session_state.get('my_profile'):
        members = st.session_state['team_rooms'][team_code]["members"]
        if st.session_state['my_profile'] not in members:
            members.append(st.session_state['my_profile'])
            st.success(f"{st.session_state['my_profile']['name']}님이 팀플방에 입장했습니다!")

    # 팀원 리스트
    st.subheader("👥 팀플방 팀원")
    for mem in st.session_state['team_rooms'][team_code]["members"]:
        st.write(f"이름: {mem['name']}, 가능 시간: {mem['times']}")
        if mem['img']:
            st.image(mem['img'], width=150, caption=f"{mem['name']} 시간표")

    # --------------------------
    # 채팅방
    # --------------------------
    st.subheader("💬 팀플 채팅방")
    if 'chat_input' not in st.session_state:
        st.session_state['chat_input'] = ''
    chat_text = st.text_input("메시지 입력", key="chat_box")
    if st.button("채팅 전송"):
        sender = st.session_state['my_profile']['name'] if st.session_state.get('my_profile') else "익명"
        msg = {"user": sender, "text": chat_text, "time": datetime.now().strftime('%H:%M')}
        st.session_state['team_rooms'][team_code]["chats"].append(msg)
    for msg in st.session_state['team_rooms'][team_code]["chats"][-8:]:
        st.write(f"[{msg['time']}] {msg['user']}: {msg['text']}")

    # --------------------------
    # 겹치는 시간 추천
    # --------------------------
    st.subheader("⏰ 겹치는 시간 자동 추천")
    all_times = [set(mem['times']) for mem in st.session_state['team_rooms'][team_code]["members"] if mem['times']]
    if all_times:
        common = set.intersection(*all_times) if len(all_times) > 1 else all_times[0]
        if common:
            st.success(f"모든 팀원이 가능한 시간: {', '.join(common)}")
        else:
            st.warning("모든 팀원이 완전히 겹치는 시간대가 없습니다. (시간 선택을 다시 확인!)")
    else:
        st.info("모든 팀원이 가능한 시간을 선택해야 추천이 가능합니다.")

st.divider()

# ----------------------------------
# 4. 네이버 지도 연동
# ----------------------------------
st.header("📍 근처 팀플 장소 추천 (네이버 지도)")

lat, lng = 37.45161, 127.12754
search_query = st.text_input("지도에서 장소 직접 검색(예: 가천대, 카페, 스터디룸 등)", value="가천대학교")
map_iframe = f"""
<iframe
  src="https://map.naver.com/p/search/{search_query}"
  width="100%"
  height="400"
  frameborder="0"
  style="border:0;"
  allowfullscreen
></iframe>
"""
st.markdown(map_iframe, unsafe_allow_html=True)
st.info("장소명을 바꿔 검색하면 다양한 주변 장소를 바로 볼 수 있습니다.")
