import streamlit as st
import google.generativeai as genai
import time

# --- UI SETUP ---
st.set_page_config(page_title="TalentScout Gemini 3", page_icon="⚡")

with st.sidebar:
    st.title("🔑 Configuration")
    user_api_key = st.text_input("Enter Gemini API Key", type="password")
    if st.button("Reset App"):
        st.session_state.clear()
        st.rerun()

# --- INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state.step = "greeting"
    st.session_state.candidate_data = {}
    st.session_state.questions = None

def get_gemini_3_response(prompt, api_key, retries=2):
    try:
        genai.configure(api_key=api_key)
        # Using the correct Gemini 3 Flash identifier
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        # Request low thinking level for instant results
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.5,
                "top_p": 0.9,
            }
        )
        return response.text
    except Exception as e:
        # Simple backoff if quota is hit
        if "429" in str(e) and retries > 0:
            time.sleep(2)
            return get_gemini_3_response(prompt, api_key, retries - 1)
        return f"Error: {str(e)}"

st.title("⚡ TalentScout (Gemini 3 Flash)")

if not user_api_key:
    st.warning("Please enter your Gemini API Key in the sidebar to begin.")
    st.stop()

# --- APP FLOW ---
if st.session_state.step == "greeting":
    st.write("### Welcome!")
    st.info("Using Gemini 3 Flash for near-instant question generation.")
    if st.button("Start Screening"):
        st.session_state.step = "info_gathering"
        st.rerun()

elif st.session_state.step == "info_gathering":
    with st.form("user_details"):
        name = st.text_input("Candidate Name")
        tech = st.text_area("Tech Stack (e.g. React, Python, SQL)")
        exp = st.number_input("Years of Experience", min_value=0)
        
        if st.form_submit_button("Generate Questions"):
            if name and tech:
                st.session_state.candidate_data = {"name": name, "tech": tech, "exp": exp}
                st.session_state.step = "tech_questions"
                st.rerun()
            else:
                st.error("Please provide both Name and Tech Stack.")

elif st.session_state.step == "tech_questions":
    st.write(f"### Screening Questions for {st.session_state.candidate_data['name']}")
    
    if st.session_state.questions is None:
        with st.spinner("Gemini 3 Flash is generating..."):
            prompt = f"""
            You are a technical interviewer. 
            Generate 3 interview questions for a candidate with {st.session_state.candidate_data['exp']} years of experience 
            in {st.session_state.candidate_data['tech']}. 
            Be concise and focus on practical application.
            """
            result = get_gemini_3_response(prompt, user_api_key)
            st.session_state.questions = result
            st.rerun()

    st.markdown(st.session_state.questions)
    
    if st.button("Finish"):
        st.session_state.step = "end"
        st.rerun()

elif st.session_state.step == "end":
    st.success("Questions successfully generated!")
    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()
