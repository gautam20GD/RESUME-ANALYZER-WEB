import streamlit as st
import pandas as pd
import os, re, hashlib, datetime, time, requests
import pdfplumber
import pymysql
import plotly.express as px
from streamlit_lottie import st_lottie

from Courses import (
    ds_course, web_course, android_course,
    ios_course, uiux_course, resume_videos
)

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# ================== ADMIN CONFIG ==================
ADMIN_USERNAME = "gautam"
ADMIN_PASSWORD_HASH = hashlib.sha256("gdbhai123".encode()).hexdigest()

# ================== DATABASE ==================
connection = pymysql.connect(
    host="localhost",
    user="root",
    password="1010gautam2020papa@2005",
    db="cv"
)
cursor = connection.cursor()

# ================== LOAD LOTTIE ==================
def load_lottie(url):
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

resume_anim = load_lottie("https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json")
admin_anim  = load_lottie("https://assets10.lottiefiles.com/packages/lf20_49rdyysj.json")

# ================== FUNCTIONS ==================
import base64

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        pdf_bytes = f.read()
        base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

    pdf_display = f"""
    <iframe
        src="data:application/pdf;base64,{base64_pdf}"
        width="100%"
        height="600"
        style="border-radius:12px;border:1px solid #22c55e;"
    ></iframe>
    """
    st.markdown(pdf_display, unsafe_allow_html=True)


def parse_resume(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            if p.extract_text():
                text += p.extract_text()

    email = re.search(r"\S+@\S+", text)
    phone = re.search(r"\+?\d[\d\s-]{8,}\d", text)

    skills_db = [
        "python","java","sql","html","css","javascript",
        "machine learning","data science","django","flask",
        "android","ios","ui","ux","react","node"
    ]

    skills = [s for s in skills_db if s in text.lower()]

    return {
        "email": email.group() if email else "N/A",
        "phone": phone.group() if phone else "N/A",
        "skills": list(set(skills)),
        "pages": max(1, len(text)//1800)
    }

def resume_score(skills, pages):
    score = 20
    score += min(len(skills)*8, 40)
    score += 20 if pages <= 2 else 10
    return min(score, 100)

def resume_level(score):
    if score < 40: return "Beginner"
    if score < 70: return "Intermediate"
    return "Advanced"

def improvement_suggestions(skills, pages, score):
    tips = []

    if score < 40:
        tips += [
            "Add more technical skills",
            "Include 2–3 real projects",
            "Use a clean professional format"
        ]
    elif score < 70:
        tips += [
            "Improve project explanations",
            "Add advanced tools & frameworks"
        ]
    else:
        tips.append("Resume is strong — focus on internships & certifications")

    if pages > 2:
        tips.append("Reduce resume length to 1–2 pages")

    for must in ["python", "sql", "projects"]:
        if must not in skills:
            tips.append(f"Consider adding {must}")

    return tips

def recommend(skills):
    if "python" in skills:
        return "Data Science", ds_course[:5]
    if "html" in skills:
        return "Web Development", web_course[:5]
    if "android" in skills:
        return "Android", android_course[:5]
    if "ui" in skills:
        return "UI/UX", uiux_course[:5]
    return "General IT", resume_videos[:5]

def insert_db(data):
    sql = """INSERT INTO user_data
    VALUES (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    cursor.execute(sql, data)
    connection.commit()

# ================== CSS (ANIMATED BACKGROUND) ==================
st.markdown("""
<style>

/* ===== PREMIUM PRINTED BACKGROUND ===== */
.stApp {
    background:
        radial-gradient(circle at top left, #1e3c72, transparent 60%),
        radial-gradient(circle at bottom right, #2a5298, transparent 60%),
        linear-gradient(135deg, #0f172a, #020617);
    color: #e5e7eb;
}

/* ===== MAIN TITLE ===== */
.big {
    font-size: 46px;
    font-weight: 900;
    color: #22c55e;
    text-align: center;
    margin-bottom: 15px;
    text-shadow: 0 0 12px rgba(34,197,94,0.6);
}

/* ===== GLASS CARD ===== */
.card {
    background: rgba(15,23,42,0.85);
    border-radius: 18px;
    padding: 26px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 20px 40px rgba(0,0,0,0.6);
}

/* ===== TEXT FIX ===== */
h1,h2,h3,h4,h5,p,span,label {
    color: #e5e7eb !important;
}

/* ===== BUTTON ===== */
button {
    background: linear-gradient(135deg,#22c55e,#16a34a) !important;
    color: black !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}

/* ===== FILE UPLOADER ===== */
section[data-testid="stFileUploader"] {
    background: rgba(30,41,59,0.9);
    padding: 15px;
    border-radius: 14px;
    border: 1px dashed #22c55e;
}

/* ===== METRIC BOX ===== */
div[data-testid="metric-container"] {
    background: rgba(2,6,23,0.85);
    border-radius: 16px;
    padding: 16px;
    border: 1px solid rgba(255,255,255,0.1);
}

</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown("<div class='big'>📄 AI Resume Analyzer</div>", unsafe_allow_html=True)

mode = st.sidebar.selectbox("Select Mode", ["User", "Admin"])

# ================== USER ==================
if mode == "User":

    st.markdown("## 👤 Resume Analysis Dashboard")

    col1, col2 = st.columns([2.3, 1])

    # ---------- LEFT : Upload Card ----------
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 📤 Upload Resume (PDF)")
        pdf = st.file_uploader("", type=["pdf"])
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- RIGHT : Animation ----------
    with col2:
        st_lottie(resume_anim, height=260)

    # ---------- AFTER UPLOAD ----------
    if pdf:
        # Save PDF
        os.makedirs("Uploaded_Resumes", exist_ok=True)
        path = f"Uploaded_Resumes/{pdf.name}"
        with open(path, "wb") as f:
            f.write(pdf.getbuffer())

        # ---------- PDF PREVIEW ----------
        st.markdown("### 📄 Resume Preview")
        show_pdf(path)

        # ---------- ANALYSIS ----------
        st.markdown("### 🔍 Analyzing Your Resume")

        progress_text = st.empty()
        progress_bar = st.progress(0)

        steps = [
            "Reading resume 📄",
            "Extracting skills 🧠",
            "Analyzing structure 📊",
            "Calculating score ⚡",
            "Generating recommendations 🎯"
        ]

        for i in range(100):
            time.sleep(0.02)
            progress_bar.progress(i + 1)
            if i % 20 == 0 and i // 20 < len(steps):
                progress_text.info(steps[i // 20])

        progress_text.success("Analysis Complete ✅")

        # ---------- LOGIC ----------
        data = parse_resume(path)
        score = resume_score(data["skills"], data["pages"])
        level = resume_level(score)
        field, courses = recommend(data["skills"])
        suggestions = improvement_suggestions(
            data["skills"],
            data["pages"],
            score
        )

        # ---------- DATABASE ----------
        insert_db((
            "User",
            data["email"],
            score,
            datetime.datetime.now(),
            data["pages"],
            field,
            level,
            ", ".join(data["skills"]),
            "Improve skills",
            ", ".join(courses)
        ))

        # ---------- RESULTS ----------
        st.markdown("---")
        st.success("🎉 Resume Analyzed Successfully")

        c1, c2, c3 = st.columns(3)
        c1.metric("📈 Score", f"{score}/100")
        c2.metric("🧑‍🎓 Level", level)
        c3.metric("🎯 Domain", field)

        # ---------- SKILLS ----------
        st.markdown("### 🧠 Extracted Skills")
        if data["skills"]:
            for s in data["skills"]:
                st.success(s)
        else:
            st.warning("No strong technical skills detected")

        # ---------- SUGGESTIONS ----------
        st.markdown("### 🛠 Improvement Suggestions")
        for s in suggestions:
            st.info(s)

        # ---------- COURSES ----------
        st.markdown("### 📚 Recommended Courses")
        for c in courses:
            st.write("👉", c)
            
# ================== ADMIN ==================
else:
    st.markdown("## 🔐 Admin Panel")

    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if u == ADMIN_USERNAME and hashlib.sha256(p.encode()).hexdigest() == ADMIN_PASSWORD_HASH:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:
        st.success("Welcome Admin 👑")

        cursor.execute("SELECT * FROM user_data")
        rows = cursor.fetchall()

        if rows:
            df = pd.DataFrame(rows, columns=[
                "ID","Name","Email","Score","Time","Pages",
                "Field","Level","Skills","RecSkills","Courses"
            ])

            st.dataframe(df, use_container_width=True)

            fig = px.pie(df, names="Field", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No records found")
