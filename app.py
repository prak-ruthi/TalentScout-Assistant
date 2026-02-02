import streamlit as st
import google.generativeai as genai

# --- UI SETUP ---
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖")

# --- SIDEBAR: API KEY MANAGEMENT ---
with st.sidebar:
    st.title("🔑 Configuration")
    user_api_key = st.text_input(
        "Enter Gemini API Key", 
        type="password", 
        help="Get your key from https://aistudio.google.com/"
    )
    st.info("Your key is used only for this session.")

# --- SESSION STATE INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state.step = "greeting"
    st.session_state.candidate_data = {}
    st.session_state.questions = None

# --- LLM CONFIGURATION ---
# We wrap this in a function so it only runs when we actually have a key
def get_llm_response(prompt, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

st.title("🤖 TalentScout Hiring Assistant")

# --- CHATBOT LOGIC ---
if st.session_state.step == "greeting":
    st.write("### Welcome to TalentScout!")
    if st.button("Start Screening"):
        st.session_state.step = "info_gathering"
        st.rerun()

elif st.session_state.step == "info_gathering":
    with st.form("info_form"):
        st.write("### Candidate Information")
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        tech = st.text_area("Tech Stack")
        exp = st.number_input("Years of Experience", min_value=0)
        
        submitted = st.form_submit_button("Submit & Generate Questions")
        
        if submitted:
            if not user_api_key:
                st.error("Please enter your API Key in the sidebar first!")
            elif not name or not tech:
                st.error("Please fill in Name and Tech Stack.")
            else:
                st.session_state.candidate_data = {"name": name, "tech": tech, "exp": exp}
                st.session_state.step = "tech_questions"
                st.rerun()

elif st.session_state.step == "tech_questions":
    st.write(f"### Technical Screening for {st.session_state.candidate_data['name']}")
    
    # Check for API key again to be safe
    if not user_api_key:
        st.warning("⚠️ API Key missing. Please enter it in the sidebar.")
        st.stop()

    if st.session_state.questions is None:
        with st.spinner("Generating questions..."):
            prompt = f"Generate 3 technical questions for a candidate with {st.session_state.candidate_data['exp']} years exp in {st.session_state.candidate_data['tech']}."
            # We pass the key directly into the function here
            result = get_llm_response(prompt, user_api_key)
            
            # Check if the response itself is an error message
            if "Error:" in result:
                st.error(result)
                if st.button("Try Again with New Key"):
                    st.session_state.questions = None
                    st.rerun()
            else:
                st.session_state.questions = result

    if st.session_state.questions:
        st.write(st.session_state.questions)
    
    if st.button("Finish & Exit"):
        st.session_state.step = "end"
        st.rerun()

elif st.session_state.step == "end":
    st.success("Screening complete!")
    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()
