
import streamlit as st
import pandas as pd
import base64
import time
import datetime
import io
import os
import hashlib

#from pyresparser import ResumeParser
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import TextConverter

from PIL import Image
import pymysql
import plotly.express as px
import nltk

from Courses import (
    ds_course, web_course, android_course,
    ios_course, uiux_course, resume_videos, interview_videos
)

nltk.download('stopwords')

# ================== CONFIG ==================

ADMIN_USERNAME = "gautam"
ADMIN_PASSWORD_HASH = hashlib.sha256("gdbhai123".encode()).hexdigest()

DEV_NAME = "Gautam Dharviya"
DEV_LINKEDIN = "https://www.linkedin.com/in/gautam-dharviya-185761292"
DEV_EMAIL = "gautamdharviya20@gmail.com"
DEV_PHONE = "9302700237"

# ================= DATABASE =================

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='1010gautam2020papa@2005',
    db='cv'
)
cursor = connection.cursor()

# ================= SESSION ==================

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ================= FUNCTIONS =================

def get_table_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'

def pdf_reader(file):
    rsrcmgr = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(rsrcmgr, fake_file_handle, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, converter)

    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh):
            interpreter.process_page(page)

    text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode()

    st.markdown(
        f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="900"></iframe>',
        unsafe_allow_html=True
    )

def insert_data(data):
    sql = """INSERT INTO user_data
    VALUES (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    cursor.execute(sql, data)
    connection.commit()

# ================= PAGE CONFIG =================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄"
)

# ================= UI =================

st.title("AI Resume Analyzer")

st.sidebar.markdown("### Choose Mode")
choice = st.sidebar.selectbox("", ["User", "Admin"])

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"""
    👨‍💻 {DEV_NAME}  
    🔗 {DEV_LINKEDIN}  
    📧 {DEV_EMAIL}  
    📞 {DEV_PHONE}
    """
)

# ================= USER =================

if choice == "User":
    st.subheader("Upload your Resume (PDF)")
    pdf_file = st.file_uploader("", type=["pdf"])

    if pdf_file:
        os.makedirs("Uploaded_Resumes", exist_ok=True)
        path = f"Uploaded_Resumes/{pdf_file.name}"

        with open(path, "wb") as f:
            f.write(pdf_file.getbuffer())

       # show_pdf(path)

      #  resume_data = ResumeParser(path).get_extracted_data()

      #  if resume_data:
        #    st.success(f"Hello {resume_data.get('name','User')} 👋")
    st.success("PDF UPLOAD SUCCESS")
# ================= ADMIN =================

else:
    if not st.session_state.admin_logged_in:
        st.subheader("Admin Login")

        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            if (
                user == ADMIN_USERNAME
                and hashlib.sha256(pwd.encode()).hexdigest() == ADMIN_PASSWORD_HASH
            ):
                st.session_state.admin_logged_in = True
                st.success("Welcome Gautam 👑")
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("Logout"):
                st.session_state.admin_logged_in = False
                st.rerun()

        st.header("Admin Dashboard")

        cursor.execute("SELECT * FROM user_data")
        df = pd.DataFrame(cursor.fetchall(), columns=[
            'ID','Name','Email','Score','Time','Pages',
            'Field','Level','Skills','Rec Skills','Courses'
        ])

        st.dataframe(df)

        st.markdown(
            get_table_download_link(df, "users.csv", "⬇ Download Data"),
            unsafe_allow_html=True
        )

        st.subheader("Career Domain Analytics")
        fig = px.pie(df, names="Field")
        st.plotly_chart(fig)