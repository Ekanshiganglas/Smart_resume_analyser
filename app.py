# app.py
# Web interface for Smart Resume Analyzer using Streamlit

import streamlit as st
import tempfile
import os
from parser import extract_text
from extractor import extract_all
from scorer import calculate_match_score, get_matching_keywords
from suggester import get_resume_suggestions

# Configure the page
st.set_page_config(
    page_title="Smart Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# Title and description
st.title("🧠 Smart Resume Analyzer")
st.markdown("Upload a resume and paste a job description to see how well they match!")

st.markdown("---")

# Create two columns for layout
col1, col2 = st.columns(2)

# Left column: Upload Resume
with col1:
    st.header("📄 Step 1: Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose a PDF or DOCX file",
        type=["pdf", "docx"],
        help="Upload the candidate's resume"
    )
    
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")

# Right column: Job Description
with col2:
    st.header("💼 Step 2: Paste Job Description")
    job_description = st.text_area(
        "Paste the job posting here",
        height=200,
        placeholder="Example:\nSenior Software Developer\n\nRequired Skills:\n- Python\n- Django\n- React\n...",
        help="Copy and paste the full job description"
    )
    
    if job_description.strip():
        word_count = len(job_description.split())
        st.info(f"📝 Job description: {word_count} words")

st.markdown("---")

# Analyze button (centered)
col_center = st.columns([1, 1, 1])
with col_center[1]:
    analyze_button = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)

# Analysis section
if analyze_button:
    # Validation
    if uploaded_file is None:
        st.error("❌ Please upload a resume first!")
    elif job_description.strip() == "":
        st.error("❌ Please paste a job description!")
    else:
        # Show loading spinner
        with st.spinner("🔄 Analyzing resume... This may take a few seconds..."):
            
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name
                
                # Extract text from resume
                resume_text = extract_text(tmp_path)
                
                # Extract information
                info = extract_all(resume_text)
                
                # Calculate match score
                score = calculate_match_score(resume_text, job_description)
                
                # Get keyword analysis
                keywords = get_matching_keywords(resume_text, job_description)
                
                # Clean up temp file
                os.unlink(tmp_path)
                
                # ========================================
                # DISPLAY RESULTS
                # ========================================
                st.markdown("---")
                st.header("📊 Analysis Results")
                
                # Match Score (big and prominent)
                st.subheader("Overall Match Score")
                
                # Color-coded score display
                if score >= 70:
                    st.success(f"# {score}%")
                    st.success("✅ **EXCELLENT MATCH!** This candidate is highly qualified for the position.")
                elif score >= 50:
                    st.warning(f"# {score}%")
                    st.warning("⚠️ **GOOD MATCH!** Candidate meets most requirements but may need some upskilling.")
                else:
                    st.error(f"# {score}%")
                    st.error("❌ **WEAK MATCH.** Candidate may need significant additional training or experience.")
                
                # Progress bar
                st.progress(score / 100)
                
                st.markdown("---")
                
                # Two columns for skills breakdown
                skill_col1, skill_col2 = st.columns(2)
                
                with skill_col1:
                    st.subheader("✅ Matching Skills")
                    if keywords['matched']:
                        for skill in keywords['matched']:
                            st.markdown(f"- ✅ {skill}")
                    else:
                        st.info("No matching skills found")
                    
                    st.metric(
                        "Skills Match", 
                        f"{keywords['match_count']}/{keywords['total_required']}",
                        f"{round(keywords['match_count']/keywords['total_required']*100) if keywords['total_required'] > 0 else 0}%"
                    )
                
                with skill_col2:
                    st.subheader("❌ Missing Skills")
                    if keywords['missing']:
                        for skill in keywords['missing']:
                            st.markdown(f"- ❌ {skill}")
                    else:
                        st.success("No missing skills!")
                
                st.markdown("---")
                
                # Candidate Information
                st.subheader("👤 Candidate Information")
                
                info_col1, info_col2, info_col3 = st.columns(3)
                
                with info_col1:
                    st.metric("Name", info['name'])
                
                with info_col2:
                    st.metric("Email", info['email'])
                
                with info_col3:
                    st.metric("Phone", info['phone'])
                
                # All detected skills
                with st.expander("📋 All Detected Skills in Resume"):
                    if info['skills']:
                        skills_text = ", ".join(info['skills'])
                        st.write(skills_text)
                        st.info(f"Total: {len(info['skills'])} skills detected")
                    else:
                        st.warning("No skills detected in resume")
                
                st.markdown("---")
                
                # ========================================
                # AI SUGGESTIONS SECTION
                # ========================================
                st.header("🤖 AI-Powered Improvement Suggestions")
                
                with st.spinner("⚙️ Generating personalized suggestions..."):
                    suggestions = get_resume_suggestions(
                        resume_text,
                        job_description,
                        score,
                        keywords['matched'],
                        keywords['missing']
                    )
                
                # Display in a nice expandable box
                with st.expander("📋 View Detailed Suggestions", expanded=True):
                    st.text(suggestions)
                
                st.markdown("---")
                
                # Raw resume text preview
                with st.expander("📄 Resume Text Preview (First 1000 characters)"):
                    st.text(resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text)
                
                st.markdown("---")
                st.success("✅ Analysis complete!")
                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.error("Please make sure the file is a valid PDF or DOCX document.")

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    **Smart Resume Analyzer** helps you:
    - Compare resumes with job descriptions
    - Calculate match scores
    - Identify missing skills
    - Get AI-powered improvement suggestions
    - Make better hiring decisions
    
    ### How to Use:
    1. Upload a resume (PDF or DOCX)
    2. Paste the job description
    3. Click "Analyze Resume"
    4. Review the results!
    
    ### Features:
    - ✅ Automatic text extraction
    - ✅ Skill matching
    - ✅ Contact info extraction
    - ✅ Match score calculation
    - ✅ AI-powered suggestions
    """)
    
    st.markdown("---")
    st.markdown("**Created by:** Your Name")
    st.markdown("**Project:** Smart Resume Analyzer")
    st.markdown("**Version:** 2.0")
