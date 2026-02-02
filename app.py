import streamlit as st
import google.generativeai as genai

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="TalentScout Assistant", page_icon="🤖", layout="centered")

# --- 2. SECURE SIDEBAR ---
with st.sidebar:
    st.title("🔐 Security Settings")
    st.markdown("---")
    user_api_key = st.text_input("Enter Google Gemini API Key", type="password")
    st.info("Your key is used only for this session.")
    st.markdown("[Get a Free API Key here](https://aistudio.google.com/)")

# --- 3. SESSION STATE (FIXES THE KEYERROR) ---
if "step" not in st.session_state:
    st.session_state.step = "greeting"
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {"name": "", "tech": "", "exp": 0}
if "questions" not in st.session_state:
    st.session_state.questions = ""

# --- 4. SMART AI FUNCTION ---
def get_llm_response(prompt):
    genai.configure(api_key=user_api_key)
    # Tries multiple models to avoid the 404 error from your previous screenshot
    for model_name in ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except:
            continue
    return "❌ All models failed. Please check your API key connection."

# --- 5. APP FLOW ---
if not user_api_key:
    st.title("🤖 TalentScout Hiring Assistant")
    st.info("### Welcome! \nPlease **enter your Gemini API Key in the sidebar** to start.")
    st.stop()

st.title("🤖 TalentScout Hiring Assistant")

# STEP 1: WELCOME
if st.session_state.step == "greeting":
    st.subheader("Automated Technical Screening")
    st.write("Welcome! I will generate custom technical questions based on your profile.")
    if st.button("Start Screening"):
        st.session_state.step = "info_gathering"
        st.rerun()

# STEP 2: INFO GATHERING
elif st.session_state.step == "info_gathering":
    st.subheader("Candidate Information")
    with st.form("info_form"):
        name = st.text_input("Full Name")
        exp = st.number_input("Years of Experience", min_value=0, step=1)
        tech = st.text_area("Tech Stack (e.g., Python, SQL, NLP)")
        
        if st.form_submit_button("Generate Questions"):
            if name and tech:
                # Saving data safely into session state to avoid KeyError
                st.session_state.candidate_data = {"name": name, "tech": tech, "exp": exp}
                st.session_state.step = "tech_questions"
                st.rerun()
            else:
                st.warning("Please fill in Name and Tech Stack.")

# STEP 3: QUESTIONS (THE FIXED SECTION)
elif st.session_state.step == "tech_questions":
    data = st.session_state.candidate_data
    st.subheader(f"Technical Assessment for {data['name']}")
    
    # Using safe strings to prevent the error seen in your last screenshot
    st.info(f"Targeting: {data['tech']} ({data['exp']} years experience)")

    if not st.session_state.questions:
        with st.spinner("🤖 AI is generating questions..."):
            prompt = f"Generate 4 technical interview questions for {data['exp']} years exp in {data['tech']}."
            st.session_state.questions = get_llm_response(prompt)
    
    st.markdown(st.session_state.questions)
    if st.button("Finish"):
        st.session_state.step = "end"
        st.rerun()

# STEP 4: CONCLUSION
elif st.session_state.step == "end":
    st.success("✅ Assessment Completed.")
    if st.button("Restart"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
