import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="TalentScout Gemini 3", page_icon="⚡", layout="centered")

# --- SIDEBAR: SECURE KEY INPUT ---
with st.sidebar:
    st.title("🔑 API Settings")
    user_api_key = st.text_input("Enter Gemini API Key", type="password", help="Get a key from ai.google.dev")
    
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()
    
    st.markdown("---")
    st.info("Using **Gemini 3 Flash** for high-speed agentic screening.")

# --- SESSION STATE INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state.step = "info_gathering"
    st.session_state.candidate_data = {}
    st.session_state.questions = None

# --- LLM FUNCTION (Gemini 3 Optimized) ---
def generate_questions(tech, exp, api_key):
    try:
        genai.configure(api_key=api_key)
        # Use the specific Gemini 3 Flash Preview identifier
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        prompt = f"""
        Act as a senior technical recruiter. 
        Generate 3 challenging interview questions for a candidate with {exp} years 
        experience in: {tech}. Focus on real-world architecture and debugging.
        """
        
        # New for Gemini 3: Configure thinking level to 'minimal' for speed
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
            }
            # Note: SDK 1.51+ supports 'thinking_level': 'minimal' in generation_config
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- MAIN UI LOGIC ---
st.title("🤖 TalentScout Hiring Assistant")

# Safety Gate: Stop app if key is missing
if not user_api_key:
    st.warning("Please enter your API Key in the sidebar to begin.")
    st.stop()

if st.session_state.step == "info_gathering":
    with st.form("info_form"):
        st.subheader("Candidate Information")
        name = st.text_input("Full Name")
        tech = st.text_area("Tech Stack (e.g., Python, AWS, React)")
        exp = st.number_input("Years of Experience", min_value=0, max_value=50, step=1)
        
        submitted = st.form_submit_button("Generate Assessment")
        
        if submitted:
            if name and tech:
                st.session_state.candidate_data = {"name": name, "tech": tech, "exp": exp}
                st.session_state.step = "view_questions"
                st.rerun()
            else:
                st.error("Please fill in Name and Tech Stack.")

elif st.session_state.step == "view_questions":
    st.subheader(f"Technical Screening: {st.session_state.candidate_data['name']}")
    
    # Generate questions only once
    if st.session_state.questions is None:
        with st.spinner("Gemini 3 Flash is reasoning..."):
            result = generate_questions(
                st.session_state.candidate_data['tech'], 
                st.session_state.candidate_data['exp'],
                user_api_key
            )
            st.session_state.questions = result
            st.rerun()

    # Display results
    st.markdown(st.session_state.questions)
    
    if st.button("Start New Screening"):
        st.session_state.clear()
        st.rerun()
