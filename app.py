import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖")

# --- SIDEBAR: SECURE KEY INPUT ---
with st.sidebar:
    st.title("🔑 API Settings")
    # Using type="password" hides the key from shoulder-surfers
    user_api_key = st.text_input("Enter your Gemini API Key", type="password")
    st.info("Your key is stored in your current browser session only.")
    
    if st.button("Clear Session"):
        st.session_state.clear()
        st.rerun()

# --- SECURITY GATE ---
# If no key is provided, show a welcome screen and STOP the script.
if not user_api_key:
    st.title("🤖 Welcome to TalentScout")
    st.warning("To begin, please enter your Gemini API Key in the sidebar.")
    st.markdown("""
    1. Go to [Google AI Studio](https://aistudio.google.com/)
    2. Click **'Get API Key'**
    3. Paste it in the box on the left 👈
    """)
    st.stop()

# --- INITIALIZATION (Only runs if key exists) ---
if "step" not in st.session_state:
    st.session_state.step = "info_gathering"
    st.session_state.candidate_data = {}

# --- HELPER FUNCTION ---
def get_ai_response(prompt):
    try:
        genai.configure(api_key=user_api_key)
        # Gemini 3 Flash is faster and less likely to "hang"
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- MAIN APP LOGIC ---
st.title("🚀 TalentScout Screening")

if st.session_state.step == "info_gathering":
    with st.form("info_form"):
        name = st.text_input("Candidate Name")
        tech = st.text_area("Tech Stack")
        submitted = st.form_submit_button("Generate Interview Questions")
        
        if submitted:
            if name and tech:
                st.session_state.candidate_data = {"name": name, "tech": tech}
                st.session_state.step = "tech_questions"
                st.rerun()

elif st.session_state.step == "tech_questions":
    st.write(f"### Questions for {st.session_state.candidate_data['name']}")
    
    # Check if questions already exist to avoid re-generating on every click
    if "questions" not in st.session_state:
        with st.spinner("AI is crafting questions..."):
            prompt = f"Generate 3 technical questions for {st.session_state.candidate_data['tech']}."
            st.session_state.questions = get_ai_response(prompt)
    
    st.write(st.session_state.questions)
    
    if st.button("Start Over"):
        st.session_state.clear()
        st.rerun()
