# TalentScout App
import streamlit as st
import google.generativeai as genai
import re

# --- CONFIGURATION ---
# Replace with your actual Gemini API Key
API_KEY = "YOUR_GEMINI_API_KEY"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- SESSION STATE INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state.step = "greeting"
    st.session_state.candidate_data = {}
    st.session_state.chat_history = []

def get_llm_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- UI SETUP ---
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖")
st.title("🤖 TalentScout Hiring Assistant")

# --- CHATBOT LOGIC ---
if st.session_state.step == "greeting":
    st.write("### Welcome to TalentScout!")
    st.info("I am your automated assistant. I'll gather some basic info and then ask a few technical questions based on your skills.")
    if st.button("Start Screening"):
        st.session_state.step = "info_gathering"
        st.rerun()

elif st.session_state.step == "info_gathering":
    with st.form("info_form"):
        st.write("### Candidate Information")
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        exp = st.number_input("Years of Experience", min_value=0, max_value=50)
        pos = st.text_input("Desired Position(s)")
        loc = st.text_input("Current Location")
        tech = st.text_area("Tech Stack (e.g., Python, Django, AWS)")
        
        submitted = st.form_submit_button("Submit & Generate Questions")
        
        if submitted:
            if not name or not email or not tech:
                st.error("Please provide at least Name, Email, and Tech Stack.")
            else:
                st.session_state.candidate_data = {
                    "name": name, "email": email, "tech": tech, "exp": exp
                }
                st.session_state.step = "tech_questions"
                st.rerun()

elif st.session_state.step == "tech_questions":
    st.write(f"### Technical Screening for {st.session_state.candidate_data['name']}")
    
    # Prompt Engineering for Question Generation
    tech_stack = st.session_state.candidate_data['tech']
    prompt = f"""
    You are a technical recruiter. Generate 3 to 5 challenging technical interview questions 
    for a candidate with {st.session_state.candidate_data['exp']} years of experience 
    proficient in the following tech stack: {tech_stack}. 
    Ensure the questions assess deep proficiency. Format as a numbered list.
    """
    
    if "questions" not in st.session_state:
        with st.spinner("Generating questions..."):
            st.session_state.questions = get_llm_response(prompt)
    
    st.write(st.session_state.questions)
    
    if st.button("Finish & Exit"):
        st.session_state.step = "end"
        st.rerun()

elif st.session_state.step == "end":
    st.success("Thank you for completing the initial screening!")
    st.write("Our recruitment team will review your profile and the generated technical assessment. We will contact you at your provided email shortly.")
    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()
