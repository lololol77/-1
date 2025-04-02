import streamlit as st
import sqlite3
import pandas as pd
import zipfile
import io

# DB 다운로드 버튼 추가 (압축 파일로 비밀번호 설정)
def download_db():
    # 압축 파일을 메모리 버퍼에 저장
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zf:
        zf.writestr('petitions.db', open('petitions.db', 'rb').read())
        # 비밀번호 설정 (777)
        zf.setpassword(b'777')
    buffer.seek(0)

    st.download_button(
        label="📂 DB 파일 다운로드",
        data=buffer,
        file_name="petitions.zip",
        mime="application/zip"
    )

# Streamlit 애플리케이션
st.title("공개 청원 작성 및 좋아요 사이트")

menu = ["청원 작성", "청원 목록", "DB 다운로드"]
choice = st.sidebar.selectbox("메뉴", menu)

if choice == "DB 다운로드":
    st.header("DB 파일 다운로드")
    download_db()



