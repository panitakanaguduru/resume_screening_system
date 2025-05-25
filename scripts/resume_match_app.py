#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# ------------------ Config ------------------
st.set_page_config(page_title="Resume Screening", layout="wide")
st.markdown("<h1>📄 Intelligent Resume Screening System</h1>", unsafe_allow_html=True)

DATA_PATH = "../data/role_match_results.csv"
RESUME_FOLDER = "../data/resumes"

# ------------------ Load Data ------------------
df = pd.read_csv(DATA_PATH)
role_cols = [col for col in df.columns if col.endswith("Score (%)")]

# ------------------ Sidebar ------------------
st.sidebar.title("⚙️ Settings")

# Dark mode toggle
dark_mode = st.sidebar.checkbox("🌙 Enable Dark Mode")
if dark_mode:
    st.markdown("<style>body { background-color: #1e1e1e; color: white; }</style>", unsafe_allow_html=True)

# Weight sliders
sim_weight = st.sidebar.slider("🧠 Similarity Weight (%)", 0, 100, 70)
skill_weight = 100 - sim_weight
st.sidebar.write(f"🔧 Skill Weight: {skill_weight}%")

# Threshold slider
min_score = st.sidebar.slider("🔍 Minimum Final Score (%)", 0, 100, 15)

# Upload new JD for matching
st.sidebar.markdown("📄 Upload Custom Job Description")
uploaded_jd = st.sidebar.file_uploader("Upload .txt file", type="txt")

# ------------------ Role Select ------------------
selected_role = st.selectbox("🎯 Select Job Role", role_cols)

# ------------------ Top Matches ------------------
top_resumes = df[["filename", selected_role]].copy()
top_resumes = top_resumes.sort_values(by=selected_role, ascending=False).reset_index(drop=True)
top_resumes = top_resumes[top_resumes[selected_role] >= min_score]

st.markdown(f"### 🏆 Top Match Score: **{top_resumes[selected_role].max():.2f}%**")
st.markdown(f"### 🔍 Top 5 Resumes for **{selected_role}**")

styled_top = top_resumes.head(5).style.format({selected_role: "{:.2f}"}).bar(subset=selected_role, color='#c4f1c4')
st.dataframe(styled_top, use_container_width=True)

# ------------------ Score Breakdown ------------------
with st.expander("📊 Resume Score Breakdown Table"):
    st.dataframe(df[["filename"] + role_cols], use_container_width=True)

# ------------------ Resume Preview ------------------
st.markdown("### 🧾 Resume Text Snippet Preview")
for filename in top_resumes["filename"].head(5):
    resume_path = os.path.join(RESUME_FOLDER, filename)
    if os.path.exists(resume_path):
        with open(resume_path, "r", errors="ignore") as file:
            text = file.read(500)
            with st.expander(f"📄 {filename} Preview"):
                st.write(text + " ...")

# ------------------ Role Comparison ------------------
st.markdown("### 📊 Multi-Role Resume Match Comparison")
st.bar_chart(df[role_cols].head(5).set_index(df["filename"].head(5)))

# ------------------ Role-wise Match Distribution ------------------
st.markdown("### 📈 Role-wise Resume Match Distribution")
fig, ax = plt.subplots()
df[role_cols].mean().sort_values().plot(kind="barh", ax=ax, color="skyblue")
ax.set_xlabel("Average Match Score (%)")
ax.set_title("Average Resume Match by Role")
st.pyplot(fig)

# ------------------ Download Buttons ------------------
st.markdown("### 📥 Download Top 5 as CSV")
csv = top_resumes.head(5).to_csv(index=False).encode('utf-8')
st.download_button("⬇️ Download CSV", data=csv, file_name=f"{selected_role}_top5.csv", mime='text/csv')

st.markdown("### 📥 Download Top 5 Resumes (PDF)")
for filename in top_resumes["filename"].head(5):
    resume_path = os.path.join(RESUME_FOLDER, filename)
    if os.path.exists(resume_path):
        with open(resume_path, "rb") as file:
            st.download_button(
                label=f"📄 {filename}",
                data=file,
                file_name=filename,
                mime="application/pdf"
            )

# ------------------ Summary Stats ------------------
st.markdown("### 🧮 Summary Panel")
st.metric("📂 Total Resumes", len(df))
st.metric("📊 Avg Match (%)", f"{df[selected_role].mean():.2f}")
st.metric("🏅 Top Score (%)", f"{df[selected_role].max():.2f}")

# ------------------ Footer ------------------
st.markdown("<hr><center><small>Made with ❤️ by <strong>Panita Vaishnavi</strong></small></center>", unsafe_allow_html=True)

