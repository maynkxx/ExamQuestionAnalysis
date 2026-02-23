import streamlit as st
from PIL import Image
import os

st.set_page_config(page_title="Exam Analysis Dashboard", layout="wide")

st.title("📊 Student Exam Analysis Dashboard")
st.markdown("This dashboard shows the performance analysis of students based on the generated reports.")

# Correct base path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.join(BASE_DIR, "reports", "plots")

# Sidebar navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio(
    "Go to",
    ["Avg score per question", "Pass vs Discrimination", "Quality Distribution", "Score Distribution"]
)

# 1️⃣ Avg score per question
if section == "Avg score per question":
    st.header("Average Score per Question")

    img_path = os.path.join(PLOT_DIR, "avg_score_per_question.png")
    img = Image.open(img_path)
    st.image(img, width="stretch")

# 2️⃣ Pass vs Discrimination
elif section == "Pass vs Discrimination":
    st.header("Pass vs Discrimination Analysis")

    img_path = os.path.join(PLOT_DIR, "pass_vs_discrimination.png")
    img = Image.open(img_path)
    st.image(img, width="stretch")

# 3️⃣ Quality Distribution
elif section == "Quality Distribution":
    st.header("Question Quality Distribution")

    img_path = os.path.join(PLOT_DIR, "quality_distribution.png")
    img = Image.open(img_path)
    st.image(img, width="stretch")

# 4️⃣ Score Distribution
elif section == "Score Distribution":
    st.header("Score Distribution")

    img_path = os.path.join(PLOT_DIR, "score_distribution.png")
    img = Image.open(img_path)
    st.image(img,width="stretch")