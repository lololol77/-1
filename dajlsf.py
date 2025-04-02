import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# 데이터베이스 초기화
conn = sqlite3.connect('petitions.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS petitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    date TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    email TEXT NOT NULL
)''')
c.execute('''CREATE TABLE IF NOT EXISTS likes (
    petition_id INTEGER,
    user_id TEXT,
    UNIQUE(petition_id, user_id)
)''')
conn.commit()

# 청원 등록 함수
def add_petition(title, content, email):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO petitions (title, content, date, likes, email) VALUES (?, ?, ?, 0, ?)', (title, content, date, email))
    conn.commit()
    # 데이터 CSV 파일로 저장
    df = pd.read_sql_query("SELECT * FROM petitions", conn)
    df.to_csv("petitions.csv", index=False)

# 좋아요 증가 함수
def like_petition(petition_id, user_id):
    try:
        c.execute('INSERT INTO likes (petition_id, user_id) VALUES (?, ?)', (petition_id, user_id))
        c.execute('UPDATE petitions SET likes = likes + 1 WHERE id = ?', (petition_id,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# 청원 조회 함수
def get_petitions(order_by='date'):
    if order_by == 'likes':
        c.execute('SELECT * FROM petitions ORDER BY likes DESC, date DESC')
    else:
        c.execute('SELECT * FROM petitions ORDER BY date DESC')
    return c.fetchall()

# Streamlit 애플리케이션
st.title("공개 청원 작성 및 좋아요 사이트")

menu = ["청원 작성", "청원 목록"]
choice = st.sidebar.selectbox("메뉴", menu)

if choice == "청원 작성":
    st.header("새로운 청원 작성하기")
    title = st.text_input("청원 제목")
    content = st.text_area("청원 내용")
    email = st.text_input("이메일 주소")
    if st.button("제출"):
        if title and content and email:
            add_petition(title, content, email)
            st.success("청원이 성공적으로 등록되었습니다!")
        else:
            st.error("제목, 내용, 이메일을 모두 입력해주세요.")

elif choice == "청원 목록":
    st.header("등록된 청원 목록")
    order_by = st.selectbox("정렬 기준", ["최신순", "좋아요순"])
    petitions = get_petitions(order_by='likes' if order_by == "좋아요순" else 'date')
    user_id = st.session_state.get("user_id", str(st.session_state.session_id))

    for petition in petitions:
        st.subheader(petition[1])
        st.write(petition[2])
        st.caption(f"등록일: {petition[3]} | 좋아요: {petition[4]}")
        if st.button(f"👍 좋아요 ({petition[4]})", key=f"like_{petition[0]}"):
            if like_petition(petition[0], user_id):
                st.success("좋아요를 눌렀습니다!")
            else:
                st.warning("이미 좋아요를 눌렀습니다.")

