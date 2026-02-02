# TalentScout App
import streamlit as st
import google.generativeai as genai

# --- UI SETUP ---
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖")

# --- SIDEBAR: API KEY MANAGEMENT ---
with st.sidebar:
    st.title("🔑 Configuration")
    user_api_key = st.text_input(
        "Enter Gemini API Key", 
        type="password", 
        help="Get your key from https://aistudio.google.com/"
    )
    st.info("Your key is used only for this session and is not stored.")

# --- INITIALIZATION ---
if user_api_key:
    try:
        genai.configure(api_key=user_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash') # Using the faster 1.5-flash model
    except Exception as e:
        st.error(f"Configuration Error: {e}")
else:
    st.warning("Please enter your API Key in the sidebar to start.")
    st.stop() # Stops the app execution until a key is provided

# --- SESSION STATE INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state.step = "greeting"
    st.session_state.candidate_data = {}

def get_llm_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

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
        tech = st.text_area("Tech Stack (e.g., Python, Django, AWS)")
        exp = st.number_input("Years of Experience", min_value=0, max_value=50)
        
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
    
    tech_stack = st.session_state.candidate_data['tech']
    prompt = f"""
    You are a technical recruiter. Generate 3 to 5 challenging technical interview questions 
    for a candidate with {st.session_state.candidate_data['exp']} years of experience 
    proficient in: {tech_stack}. Format as a numbered list.
    """
    
    if "questions" not in st.session_state:
        with st.spinner("Generating questions..."):
            st.session_state.questions = get_llm_response(prompt)
    
    st.write(st.session_state.questions)
    
    if st.button("Finish & Exit"):
        st.session_state.step = "end"
        st.rerun()

elif st.session_state.step == "end":
    st.success("Screening complete!")
    if st.button("Restart"):
        # Clear specific keys but keep the API Key in the sidebar
        for key in ["step", "candidate_data", "questions"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
