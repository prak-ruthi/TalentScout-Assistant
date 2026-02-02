import streamlit as st
import google.generativeai as genai

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

def get_gemini_3_response(prompt, api_key):
    try:
        genai.configure(api_key=api_key)
        # Using the Gemini 3 Flash model
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        # Generating content with minimal thinking to prevent hangs
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.7}
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

st.title("⚡ TalentScout (Gemini 3 Flash)")

if not user_api_key:
    st.warning("Please enter your API Key in the sidebar.")
    st.stop()

# --- APP FLOW ---
if st.session_state.step == "greeting":
    st.write("Welcome! Let's generate some technical questions using Gemini 3 Flash.")
    if st.button("Start Screening"):
        st.session_state.step = "info_gathering"
        st.rerun()

elif st.session_state.step == "info_gathering":
    with st.form("user_details"):
        name = st.text_input("Candidate Name")
        tech = st.text_area("Tech Stack")
        exp = st.number_input("Years of Experience", min_value=0)
        if st.form_submit_button("Generate Questions"):
            st.session_state.candidate_data = {"name": name, "tech": tech, "exp": exp}
            st.session_state.step = "tech_questions"
            st.rerun()

elif st.session_state.step == "tech_questions":
    st.write(f"### Questions for {st.session_state.candidate_data['name']}")
    
    if st.session_state.questions is None:
        with st.spinner("Gemini 3 Flash is thinking..."):
            prompt = f"Generate 3 difficult technical interview questions for {st.session_state.candidate_data['tech']} ({st.session_state.candidate_data['exp']} years exp)."
            result = get_gemini_3_response(prompt, user_api_key)
            st.session_state.questions = result
            st.rerun()

    st.markdown(st.session_state.questions)
    
    if st.button("Finish"):
        st.session_state.step = "end"
        st.rerun()

elif st.session_state.step == "end":
    st.success("All done!")
    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()
