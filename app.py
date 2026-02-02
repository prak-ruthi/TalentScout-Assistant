import streamlit as st
import google.generativeai as genai

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="TalentScout Assistant", page_icon="🤖", layout="centered")

# --- 2. SIDEBAR SECURITY ---
with st.sidebar:
    st.title("🔐 Security Settings")
    user_api_key = st.text_input("Enter Google Gemini API Key", type="password")
    st.info("Your key is used only for this session.")
    st.markdown("[Get a Free API Key here](https://aistudio.google.com/)")

# --- 3. SMART MODEL INITIALIZATION ---
if not user_api_key:
    st.title("🤖 TalentScout Hiring Assistant")
    st.info("### Welcome! \nTo begin, please **enter your Gemini API Key in the sidebar.**")
    st.stop()

# Helper function to try multiple models automatically
def get_llm_response(prompt):
    genai.configure(api_key=user_api_key)
    # List of models to try in order of speed/availability
    model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
    
    last_error = ""
    for name in model_names:
        try:
            model = genai.GenerativeModel(name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = str(e)
            continue # Try the next model if one fails
            
    return f"❌ All models failed. Error: {last_error}"

# --- 4. SESSION STATE ---
if "step" not in st.session_state:
    st.session_state.step = "greeting"
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {}
if "questions" not in st.session_state:
    st.session_state.questions = ""

# --- 5. APP UI FLOW ---
st.title("🤖 TalentScout Hiring Assistant")

if st.session_state.step == "greeting":
    st.subheader("Automated Technical Screening")
    st.write("Welcome! This tool uses Generative AI to generate custom technical assessments.")
    if st.button("Start Screening"):
        st.session_state.step = "info_gathering"
        st.rerun()

elif st.session_state.step == "info_gathering":
    st.subheader("Candidate Information")
    with st.form("info_form"):
        name = st.text_input("Full Name")
        exp = st.number_input("Years of Experience", min_value=0, step=1)
        tech = st.text_area("Tech Stack", placeholder="e.g. Python, SQL, NLP")
        if st.form_submit_button("Generate Questions"):
            if name and tech:
                st.session_state.candidate_data = {"name": name, "tech": tech, "exp": exp}
                st.session_state.step = "tech_questions"
                st.rerun()
            else:
                st.warning("Please fill in Name and Tech Stack.")

elif st.session_state.step == "tech_questions":
    data = st.session_state.candidate_data
    st.subheader(f"Technical Assessment: {data['name']}")
    
    if not st.session_state.questions:
        with st.spinner("🤖 AI is selecting the best model for your key..."):
            prompt = f"Generate 4 technical interview questions for {data['exp']} years exp in {data['tech']}."
            st.session_state.questions = get_llm_response(prompt)
    
    st.markdown(st.session_state.questions)
    if st.button("Finish"):
        st.session_state.step = "end"
        st.rerun()

elif st.session_state.step == "end":
    st.success("✅ Assessment Completed.")
    if st.button("Restart"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
