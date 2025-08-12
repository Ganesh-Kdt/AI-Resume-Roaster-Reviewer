import streamlit as st
from utils import extract_text_from_pdf, extract_rewrites, replace_bullets_whole_text, ats_score
from openai import OpenAI
from prompts import get_roast_prompt
import re
from vision_ocr import pdf_pages_to_base64_images
from openai.types.chat import ChatCompletionMessageParam
from typing import Sequence

st.set_page_config(page_title="AI Resume Roaster", layout="centered")

st.title("🔥 AI Resume Roaster + Rewriter")
st.markdown(
    """
    Upload your resume, and pick your target job role. 
    Our AI will give honest feedback and improved bullet points tailored to your goals.
    """
)

#Upload Resume
uploaded_file = st.file_uploader("📄 Upload your resume as PDF", type=["pdf"])
if uploaded_file:
    if not uploaded_file.name.lower().endswith('.pdf'):
        st.error("Only PDF files are allowed. Please upload a PDF resume.")
        uploaded_file = None
        st.stop()
    
    if uploaded_file.type != "application/pdf":
        st.error("Invalid file type. Please upload a valid PDF file.")
        uploaded_file = None
        st.stop()
    
    max_size_mb = 10
    max_size_bytes = max_size_mb * 1024 * 1024
    if uploaded_file.size > max_size_bytes:
        st.error(f"File too large ({uploaded_file.size / (1024*1024):.1f}MB). Maximum allowed: {max_size_mb}MB")
        uploaded_file = None
        st.stop()
    
    st.success(f"✅ PDF uploaded successfully! Size: {uploaded_file.size / (1024*1024):.1f}MB")

#Job Role Dropdown
job_role = st.selectbox(
    "🎯 What job are you targeting? *",
    ["Software Engineer", "Data Scientist", "Product Manager", "UX Designer", "Cybersecurity Analyst"]
)

#Job Description Input
job_description = st.text_area(
    "📋 Job Description *",
    placeholder="Paste the job description here to get more targeted feedback. This helps the AI understand what the employer is looking for and provide better suggestions.",
    height=150
)

st.caption("Fields marked with * are required")

if uploaded_file:
    st.success("✅ Resume uploaded successfully!")
    resume_text = None
    st.info("ℹ️ PDF preview will be generated in the next step.")

    if st.button("Resume Extraction"):
        if not job_role:
            st.error("Please select a job role.")
            st.stop()
        
        if not job_description or not job_description.strip():
            st.error("Please provide a job description.")
            st.stop()
        
        with st.spinner("🔄 Processing your resume..."):
            st.session_state.resume_uploaded = True
            st.session_state.job_role = job_role
            st.session_state.job_description = job_description
            st.session_state.uploaded_file = uploaded_file
            st.success("✅ Moving to Step 2: AI Feedback...")
            st.rerun()
else:
    st.info("Please upload a resume to get started.")


# Set OpenAI API key from Streamlit secrets
api_key = st.secrets.get("OPENAI_API_KEY")
if not api_key:
    st.error("OpenAI API key not found. Please add it to your Streamlit secrets.")
    st.stop()
client = OpenAI(api_key=api_key)

def get_resume_level(score):
    """Get resume level based on score"""
    if score >= 90:
        return "Resume Legend", "gold"
    elif score >= 80:
        return "Resume Master", "orange"
    elif score >= 70:
        return "Resume Pro", "red"
    elif score >= 60:
        return "Resume Builder", "blue"
    elif score >= 50:
        return "Resume Rookie", "green"
    else:
        return "Resume Seedling", "gray"

def display_resume_score(score, level, color):
    """Display the resume score with visual elements"""
    st.markdown("---")
    st.subheader("📊 Resume Score")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Score circle
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="
                width: 120px; 
                height: 120px; 
                border-radius: 50%; 
                background: conic-gradient({color} {score * 3.6}deg, #f0f0f0 {score * 3.6}deg);
                display: flex; 
                align-items: center; 
                justify-content: center; 
                margin: 0 auto;
                border: 4px solid {color};
            ">
                <div style="
                    background: white; 
                    width: 100px; 
                    height: 100px; 
                    border-radius: 50%; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    font-size: 24px;
                    font-weight: bold;
                    color: {color};
                ">
                    {score}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Level badge
        st.markdown(f"""
        <div style="text-align: center; margin-top: 10px;">
            <span style="
                background: {color}; 
                color: white; 
                padding: 8px 16px; 
                border-radius: 20px; 
                font-weight: bold;
                font-size: 16px;
            ">
                {level}
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    # Progress bar
    st.progress(score / 100)
    st.caption(f"Progress to next level: {score}/100")

# Step 2: Run AI Roast if resume is uploaded
if st.session_state.get("resume_uploaded"):
    st.header("Step 2: AI Resume Critique + Rewrite")

    uploaded_file = st.session_state.uploaded_file
    job_role = st.session_state.job_role
    job_description = st.session_state.get("job_description", "")
    resume_text=''
    # Extract text from uploaded resume
    if uploaded_file.name.endswith('.pdf'):
        resume_text = extract_text_from_pdf(uploaded_file)

    st.subheader("🔍 Resume Extracted")
    
    with st.expander("📄 Click to view extracted resume text", expanded=False):
        st.code(resume_text)

    #MODEL SETTINGS
    st.subheader("AI Settings")
    model_choice = st.selectbox("Choose GPT Model", ["gpt-4o"])

    if st.button("🔥 Get Feedback from AI"):
        with st.spinner("AI is analyzing your resume... This may take a few moments."):
            prompt = get_roast_prompt(resume_text, job_role, job_description)

            try:
                if uploaded_file.name.lower().endswith(".pdf"):
                    uploaded_file.seek(0)  # ensure pointer at start before reading
                    pdf_bytes = uploaded_file.read()
                    if not pdf_bytes:
                        raise ValueError("Uploaded PDF appears to be empty. Please re-upload the file.")
                    img_msgs = pdf_pages_to_base64_images(pdf_bytes)
                    uploaded_file.seek(0)  # reset pointer for any later reads

                    # Build messages for vision model
                    messages = [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            *img_msgs 
                        ]
                    }]
                    messages_cast: Sequence[ChatCompletionMessageParam] = messages  # type: ignore
                    response = client.chat.completions.create(
                        model=model_choice,             
                        messages=messages_cast,
                        temperature=0.7,
                    )
                
                    feedback = response.choices[0].message.content
                    st.session_state.feedback = feedback
                    st.rerun()

            except Exception as e:
                st.error(f"Error calling OpenAI API: {e}")
    
    # Display feedback if available
    if "feedback" in st.session_state and st.session_state.feedback:
        st.subheader("📋 AI Resume Review")
        st.markdown(st.session_state.feedback)

        rewrites      = extract_rewrites(st.session_state.feedback)
        updated_text  = replace_bullets_whole_text(resume_text, rewrites)

        # Show the improved resume
        st.subheader("Updated Resume Preview")
        with st.expander("Click to view updated resume", expanded=False):
            st.code(updated_text)

        # Optional download
        st.download_button(
            "Download Updated Resume(.txt)",
            updated_text,
            file_name="updated_resume.txt",
            mime="text/plain"
        )

        # Calculate and display resume score
        score = ats_score(updated_text, job_description)
        level, color = get_resume_level(score)
        display_resume_score(score, level, color)
                
        # Reset button to get new feedback
        if st.button("Get New Feedback"):
            st.session_state.feedback = None
            st.session_state.current_score = None
            st.rerun()