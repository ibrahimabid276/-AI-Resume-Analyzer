import streamlit as st
import tempfile
from backend_simple import analyze_resume

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# Header
st.title("📄 AI Resume Analyzer")

st.divider()

# Input
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

with col2:
    job_description = st.text_area("Paste Job Description", height=200)

# Button
if st.button("🚀 Analyze Resume", use_container_width=True):

    if uploaded_file is None or job_description.strip() == "":
        st.warning("Please upload resume and enter job description.")
    else:
        with st.spinner("Analyzing..."):

            # Save PDF temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                pdf_path = tmp.name

            result = analyze_resume(pdf_path, job_description)

        st.success("Analysis Completed")

        st.divider()
        st.subheader("📊 Resume Analysis Report")

        st.markdown(result)