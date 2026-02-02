import streamlit as st
from google import genai
from google.genai import types

# --- UI SETUP ---
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖", layout="wide")

# --- SIDEBAR: API KEY ---
with st.sidebar:
    st.title("🔑 Configuration")
    user_api_key = st.text_input("Gemini API Key", type="password", help="Get your key at ai.google.dev")
    if st.button("Reset All Data"):
        st.session_state.clear()
        st.rerun()
    st.info("Using Gemini 3 Flash for near-instant generation.")

# --- INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state.step = "greeting"
    st.session_state.candidate_data = {}
    st.session_state.questions = None

# --- AGENTIC LLM FUNCTION ---
def get_gemini_3_response(prompt, api_key):
    try:
        # Latest 2026 Client initialization
        client = genai.Client(api_key=api_key)
        
        # Requesting high-speed 'Flash' response
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                # Thinking levels are handled natively by Gemini 3 Flash
            )
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

st.title("🤖 TalentScout Hiring Assistant")

# --- SECURITY GATE ---
if not user_api_key:
    st.warning("👈 Please enter your Gemini API Key in the sidebar to proceed.")
    st.stop()

# --- APP FLOW ---

# 1. GREETING
if st.session_state.step == "greeting":
    st.write("### Welcome to the TalentScout Technical Screening Tool.")
    if st.button("Start New Candidate Screening"):
        st.session_state.step = "info_gathering"
        st.rerun()

# 2. INFO GATHERING (Your Integrated Form)
elif st.session_state.step == "info_gathering":
    st.subheader("Step 2: Candidate Information")
    with st.form("info_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            phone = st.text_input("Phone Number")
        with col2:
            position = st.text_input("Desired Position(s)")
            location = st.text_input("Current Location")
            exp = st.number_input("Years of Experience", min_value=0, max_value=50, step=1)
        
        tech = st.text_area("Tech Stack (Languages, Frameworks, Tools)")
        
        submitted = st.form_submit_button("Generate Interview Questions")
        
        if submitted:
            # Check all required fields
            if not all([name, email, phone, position, location, tech]):
                st.warning("⚠️ Please fill in all details required by TalentScout.")
            else:
                st.session_state.candidate_data = {
                    "name": name, 
                    "tech": tech, 
                    "exp": exp,
                    "position": position
                }
                st.session_state.step = "tech_questions"
                st.rerun()

# 3. QUESTION GENERATION
elif st.session_state.step == "tech_questions":
    st.write(f"### Screening Assessment for **{st.session_state.candidate_data['name']}**")
    
    if st.session_state.questions is None:
        with st.spinner("AI is reasoning... (This will be fast)"):
            prompt = (f"You are a technical interviewer. Generate 3 behavioral and 3 technical "
                      f"interview questions for a {st.session_state.candidate_data['position']} candidate "
                      f"with {st.session_state.candidate_data['exp']} years of experience. "
                      f"Focus specifically on their tech stack: {st.session_state.candidate_data['tech']}.")
            
            result = get_gemini_3_response(prompt, user_api_key)
            
            if "Error" in result:
                st.error(result)
                if st.button("Retry"): st.rerun()
            else:
                st.session_state.questions = result
                st.rerun()

    st.markdown("---")
    st.markdown(st.session_state.questions)
    
    if st.button("Finish & Reset"):
        st.success("Screening session complete!")
        st.session_state.clear()
        st.rerun()
