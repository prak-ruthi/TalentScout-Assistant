import streamlit as st
import google.generativeai as genai

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="TalentScout Assistant", page_icon="🤖", layout="centered")

# --- 2. SIDEBAR FOR SECURE API KEY INPUT ---
with st.sidebar:
    st.title("🔐 Security Settings")
    st.markdown("---")
    # type="password" ensures the key is hidden while typing
    user_api_key = st.text_input("Enter Google Gemini API Key", type="password")
    st.info("Your key is only used for this session and is not stored.")
    st.markdown("[Get a Free API Key here](https://aistudio.google.com/)")

# --- 3. SMART MODEL HANDLER ---
# Pauses execution until a key is provided
if not user_api_key:
    st.title("🤖 TalentScout Hiring Assistant")
    st.info("### Welcome! \nPlease **enter your Gemini API Key in the sidebar** to start the screening.")
    st.stop()

def get_llm_response(prompt):
    """Tries multiple model versions to avoid 404/Not Found errors."""
    genai.configure(api_key=user_api_key)
    # List of models to try in order of availability
    model_versions = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
    
    last_error = ""
    for version in model_versions:
        try:
            model = genai.GenerativeModel(version)
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            last_error = str(e)
            continue # Try the next version if the current one fails
            
    return f"❌ All models failed. Technical Error: {last_error}"

# --- 4. SESSION STATE MANAGEMENT ---
if "step" not in st.session_state:
    st.session_state.step = "greeting"
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {}
if "questions" not in st.session_state:
    st.session_state.questions = ""

# --- 5. APPLICATION FLOW ---
st.title("🤖 TalentScout Hiring Assistant")

# STEP 1: WELCOME SCREEN
if st.session_state.step == "greeting":
    st.subheader("Automated Technical Screening")
    st.write("Welcome! This AI-powered tool generates custom technical assessments based on your expertise.")
    if st.button("Start Screening"):
        st.session_state.step = "info_gathering"
        st.rerun()

# STEP 2: INFORMATION COLLECTION
elif st.session_state.step == "info_gathering":
    st.subheader("Candidate Information")
    with st.form("info_form"):
        name = st.text_input("Full Name (e.g., Prakruthi B)")
        exp = st.number_input("Years of Experience", min_value=0, max_value=40, step=1)
        tech = st.text_area("Tech Stack (e.g., Python, SQL, Machine Learning)")
        
        if st.form_submit_button("Generate Assessment"):
            if name and tech:
                st.session_state.candidate_data = {"name": name, "tech": tech, "exp": exp}
                st.session_state.step = "tech_questions"
                st.rerun()
            else:
                st.warning("Please provide your Name and Tech Stack to proceed.")

# STEP 3: TECHNICAL ASSESSMENT
elif st.session_state.step == "tech_questions":
    data = st.session_state.candidate_data
    st.subheader(f"Technical Assessment for {data['name']}")
    st.info(f"Targeting: {data['tech']} ({data['exp']} years experience)")

    if not st.session_state.questions:
        with st.spinner("🤖 AI is selecting a compatible model and generating questions..."):
            prompt = f"Generate 4 challenging interview questions for a candidate with {data['exp']} years exp in {data['tech']}."
            st.session_state.questions = get_llm_response(prompt)
    
    st.markdown(st.session_state.questions)
    if st.button("Complete Assessment"):
        st.session_state.step = "end"
        st.rerun()

# STEP 4: CONCLUSION
elif st.session_state.step == "end":
    st.success("✅ Application successfully recorded. Thank you!")
    if st.button("Restart New Session"):
        # Clears all cached data to allow a fresh start
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
