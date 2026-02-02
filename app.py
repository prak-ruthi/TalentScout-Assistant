import streamlit as st
import google.generativeai as genai
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TalentScout Hiring Assistant", 
    page_icon="🤖", 
    layout="centered"
)

# --- 2. SIDEBAR FOR SECURITY ---
with st.sidebar:
    st.title("🔐 Security Settings")
    st.markdown("---")
    user_api_key = st.text_input(
        "Enter Google Gemini API Key", 
        type="password", 
        help="Paste your API key from Google AI Studio."
    )
    st.info("Your key is used only for this session and is not stored.")
    st.markdown("[Get a Free API Key here](https://aistudio.google.com/)")

# --- 3. INITIALIZE AI MODEL ---
if not user_api_key:
    st.title("🤖 TalentScout Hiring Assistant")
    st.info("### Welcome! \nTo begin, please **enter your Gemini API Key in the sidebar.**")
    st.stop()

try:
    genai.configure(api_key=user_api_key)
    # Using 'gemini-pro' as it's the most stable version for standard API keys
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

# --- 4. SESSION STATE MANAGEMENT ---
if "step" not in st.session_state:
    st.session_state.step = "greeting"
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {}
if "questions" not in st.session_state:
    st.session_state.questions = ""

# --- 5. HELPER FUNCTION ---
def get_llm_response(prompt):
    try:
        # Standard API call for maximum compatibility
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            return response.text
        else:
            return "⚠️ The AI service responded but didn't provide text. Please try again."
    except Exception as e:
        if "404" in str(e):
            return "❌ Model Not Found: Try using a different API key or check Google AI Studio settings."
        return f"⚠️ Error: {str(e)}"

# --- 6. APP UI FLOW ---
st.title("🤖 TalentScout Hiring Assistant")

# --- STEP 1: GREETING ---
if st.session_state.step == "greeting":
    st.subheader("Automated Technical Screening")
    st.write("Welcome! This tool uses Generative AI to generate custom technical assessments.")
    if st.button("Start Screening"):
        st.session_state.step = "info_gathering"
        st.rerun()

# --- STEP 2: INFO GATHERING ---
elif st.session_state.step == "info_gathering":
    st.subheader("Candidate Information")
    with st.form("info_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        exp = st.number_input("Years of Experience", min_value=0, max_value=50, step=1)
        tech = st.text_area("Tech Stack", placeholder="e.g. Python, SQL, NLP, AWS")
        
        submitted = st.form_submit_button("Generate Interview Questions")
        if submitted:
            if not name or not tech:
                st.warning("Please fill in the Name and Tech Stack.")
            else:
                st.session_state.candidate_data = {"name": name, "tech": tech, "exp": exp}
                st.session_state.step = "tech_questions"
                st.rerun()

# --- STEP 3: TECH QUESTIONS ---
elif st.session_state.step == "tech_questions":
    data = st.session_state.candidate_data
    st.subheader(f"Technical Assessment: {data['name']}")
    st.write(f"**Experience:** {data['exp']} years | **Tech Stack:** {data['tech']}")
    st.markdown("---")

    if not st.session_state.questions:
        with st.spinner("🤖 AI is generating questions..."):
            prompt = f"""
            Act as a technical interviewer. Generate 4 high-quality interview questions 
            for a candidate with {data['exp']} years of experience in {data['tech']}.
            Format with clear bullet points.
            """
            st.session_state.questions = get_llm_response(prompt)
    
    st.markdown(st.session_state.questions)
    
    if st.button("Finish & Clear"):
        st.session_state.step = "end"
        st.rerun()

# --- STEP 4: END ---
elif st.session_state.step == "end":
    st.success("✅ Application Completed Successfully.")
    st.balloons()
    if st.button("Restart New Application"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
