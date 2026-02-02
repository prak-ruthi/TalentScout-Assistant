import streamlit as st
import google.generativeai as genai

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="TalentScout Assistant", page_icon="🤖", layout="centered")

# --- 2. SECURE SIDEBAR ---
with st.sidebar:
    st.title("🔐 Security Settings")
    user_api_key = st.text_input("Enter Gemini API Key", type="password")
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()
    st.info("Your key is used only for this session and is not stored.")

# --- 3. SESSION STATE (PREVENTS KEYERRORS) ---
# We initialize all required keys to prevent the error seen in your screenshot
if "step" not in st.session_state:
    st.session_state.step = "greeting"
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {"name": "", "tech": "", "exp": 0, "pos": "", "phone": "", "loc": ""}
if "questions" not in st.session_state:
    st.session_state.questions = None

# --- 4. SMART MODEL ROUTER ---
def generate_questions(tech, exp, pos, api_key):
    genai.configure(api_key=api_key)
    # Automatically tries the newest model, then falls back to the most stable one
    # This solves the 404 error from your screenshot
    for model_name in ['gemini-1.5-flash', 'gemini-pro']:
        try:
            model = genai.GenerativeModel(model_name)
            prompt = f"Act as a senior technical recruiter. Generate 3 challenging interview questions for a {pos} with {exp} years exp in {tech}."
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            continue
    return "❌ Error: Could not connect to any available Gemini models. Please check your API key."

# --- 5. APP FLOW ---
st.title("🤖 TalentScout Hiring Assistant")

if not user_api_key:
    st.warning("Please enter your API Key in the sidebar to begin.")
    st.stop()

# STEP 1: GREETING (Requirement 1)
if st.session_state.step == "greeting":
    st.subheader("Welcome to TalentScout")
    st.write("I am your AI Recruitment Assistant. I help collect candidate profiles and generate custom technical assessments.")
    if st.button("Start Application"):
        st.session_state.step = "info_gathering"
        st.rerun()

# STEP 2: INFO GATHERING (Mandatory Fields)
elif st.session_state.step == "info_gathering":
    with st.form("info_form"):
        st.subheader("Candidate Information")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            phone = st.text_input("Phone Number")
            loc = st.text_input("Location")
        with col2:
            pos = st.text_input("Desired Position")
            exp = st.number_input("Experience (Years)", min_value=0, step=1)
            tech = st.text_area("Tech Stack")
        
        if st.form_submit_button("Generate Assessment"):
            if all([name, pos, tech]):
                st.session_state.candidate_data = {"name": name, "tech": tech, "exp": exp, "pos": pos, "phone": phone, "loc": loc}
                st.session_state.step = "view_questions"
                st.rerun()
            else:
                st.error("Please fill in Name, Position, and Tech Stack.")

# STEP 3: TECHNICAL QUESTIONS
elif st.session_state.step == "view_questions":
    data = st.session_state.candidate_data
    st.subheader(f"Technical Screening for {data['name']}")
    
    # Safe display logic to prevent KeyError crashes
    st.info(f"Targeting: {data.get('pos', 'Not Specified')} | Experience: {data.get('exp', 0)} years")

    if st.session_state.questions is None:
        with st.spinner("Analyzing profile and generating questions..."):
            st.session_state.questions = generate_questions(data['tech'], data['exp'], data['pos'], user_api_key)
            st.rerun()

    st.markdown(st.session_state.questions)
    if st.button("Finish & Exit"):
        st.session_state.step = "exit"
        st.rerun()

# STEP 4: EXIT
elif st.session_state.step == "exit":
    st.success("✅ Application Submitted Successfully!")
    st.balloons()
    st.write(f"Thank you, {st.session_state.candidate_data['name']}. Our team will contact you soon.")
    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()
