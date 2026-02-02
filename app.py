import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖", layout="centered")

# --- SIDEBAR: SECURE KEY INPUT ---
with st.sidebar:
    st.title("🔑 API Settings")
    user_api_key = st.text_input("Enter Gemini API Key", type="password", help="Get a key from ai.google.dev")
    
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()
    
    st.markdown("---")
    st.info("Agentic AI screening powered by Google Gemini.")

# --- SESSION STATE INITIALIZATION ---
# Initializing data properly to avoid the KeyError seen in your screenshot
if "step" not in st.session_state:
    st.session_state.step = "greeting"
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {"name": "", "tech": "", "exp": 0, "phone": "", "pos": "", "loc": ""}
if "questions" not in st.session_state:
    st.session_state.questions = None

# --- ROBUST LLM FUNCTION ---
def generate_questions(tech, exp, pos, api_key):
    try:
        genai.configure(api_key=api_key)
        # Fallback List: Tries newest models first, defaults to stable if 404 occurs
        for model_name in ['gemini-1.5-flash', 'gemini-pro']:
            try:
                model = genai.GenerativeModel(model_name)
                prompt = f"Act as a technical recruiter. Generate 3 interview questions for a {pos} with {exp} years exp in {tech}. Focus on architecture."
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                if "404" in str(e): continue # Try next model
                else: return f"Error: {str(e)}"
        return "❌ Error: No compatible models found for this API key."
    except Exception as e:
        return f"Error: {str(e)}"

# --- MAIN UI LOGIC ---
st.title("🤖 TalentScout Hiring Assistant")

if not user_api_key:
    st.warning("Please enter your API Key in the sidebar to begin.")
    st.stop()

# --- STEP 1: GREETING SCREEN ---
if st.session_state.step == "greeting":
    st.subheader("Welcome to TalentScout")
    st.write("""
    I am your AI Recruitment Assistant. I help streamline the screening process by 
    gathering professional details and generating custom technical assessments.
    """)
    if st.button("Start Application"):
        st.session_state.step = "info_gathering"
        st.rerun()

# --- STEP 2: INFO GATHERING (MANDATORY FIELDS) ---
elif st.session_state.step == "info_gathering":
    with st.form("info_form"):
        st.subheader("Candidate Information")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            phone = st.text_input("Phone Number")
            loc = st.text_input("Current Location")
        with col2:
            pos = st.text_input("Desired Position")
            exp = st.number_input("Years of Experience", min_value=0, step=1)
            email = st.text_input("Email Address")
        
        tech = st.text_area("Tech Stack (e.g., Python, SQL, NLP)")
        
        if st.form_submit_button("Generate Assessment"):
            if name and tech and phone and pos:
                st.session_state.candidate_data = {
                    "name": name, "tech": tech, "exp": exp, 
                    "phone": phone, "pos": pos, "loc": loc
                }
                st.session_state.step = "view_questions"
                st.rerun()
            else:
                st.error("Please fill in all mandatory fields.")

# --- STEP 3: TECHNICAL SCREENING ---
elif st.session_state.step == "view_questions":
    data = st.session_state.candidate_data
    st.subheader(f"Technical Screening: {data['name']}")
    st.caption(f"Targeting: {data['pos']} | {data['exp']} years experience")

    if st.session_state.questions is None:
        with st.spinner("Generating specialized questions..."):
            st.session_state.questions = generate_questions(data['tech'], data['exp'], data['pos'], user_api_key)
            st.rerun()

    st.markdown(st.session_state.questions)
    if st.button("Finish & Exit"):
        st.session_state.step = "exit"
        st.rerun()

# --- STEP 4: EXIT SCREEN ---
elif st.session_state.step == "exit":
    st.success("✅ Application Submitted!")
    st.balloons()
    st.write(f"Thank you, {st.session_state.candidate_data['name']}. We will contact you at {st.session_state.candidate_data['phone']}.")
    if st.button("Start New Screening"):
        st.session_state.clear()
        st.rerun()
