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
    st.info("Using Gemini Flash for high-speed technical screening.")

# --- 3. SESSION STATE (FIXES KEYERRORS) ---
# We initialize all required keys to prevent the KeyError seen in your screenshots
if "step" not in st.session_state:
    st.session_state.step = "greeting"
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {
        "name": "", "tech": "", "exp": 0, "pos": "", "phone": "", "loc": "", "email": ""
    }
if "questions" not in st.session_state:
    st.session_state.questions = None

# --- 4. SMART MODEL ROUTER (FIXES 404 ERRORS) ---
def generate_questions(tech, exp, pos, api_key):
    genai.configure(api_key=api_key)
    # Automatically tries multiple model strings to find one compatible with your key
    # This directly solves the 404 error from your screenshot
    for model_name in ['gemini-1.5-flash-latest', 'gemini-1.5-flash', 'gemini-pro']:
        try:
            model = genai.GenerativeModel(model_name)
            prompt = f"Act as a senior technical recruiter. Generate 3 challenging interview questions for a {pos} with {exp} years exp in {tech}."
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception:
            continue # Try the next model name in the list
    return "❌ Error: Could not connect to any available Gemini models. Please check your API key."

# --- 5. APP FLOW ---
st.title("🤖 TalentScout Hiring Assistant")

if not user_api_key:
    st.warning("Please enter your Gemini API Key in the sidebar to begin.")
    st.stop()

# STEP 1: GREETING (Mandatory Assignment Requirement)
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
            email = st.text_input("Email Address")
            phone = st.text_input("Phone Number")
        with col2:
            pos = st.text_input("Desired Position")
            loc = st.text_input("Current Location")
            exp = st.number_input("Experience (Years)", min_value=0, step=1)
        
        tech = st.text_area("Tech Stack (e.g., Python, AWS, React)")
        
        if st.form_submit_button("Generate Assessment"):
            if all([name, email, pos, tech]):
                st.session_state.candidate_data = {
                    "name": name, "tech": tech, "exp": exp, "pos": pos, 
                    "phone": phone, "loc": loc, "email": email
                }
                st.session_state.step = "view_questions"
                st.rerun()
            else:
                st.error("Please fill in Name, Email, Position, and Tech Stack.")

# STEP 3: TECHNICAL QUESTIONS
elif st.session_state.step == "view_questions":
    data = st.session_state.candidate_data
    st.subheader(f"Technical Screening for {data['name']}")
    
    # Safe display logic using .get() to prevent KeyError crashes
    st.info(f"Targeting: {data.get('pos')} | Experience: {data.get('exp')} years")

    if st.session_state.questions is None:
        with st.spinner("Analyzing profile and generating questions..."):
            st.session_state.questions = generate_questions(data['tech'], data['exp'], data['pos'], user_api_key)
            st.rerun()

    st.markdown(st.session_state.questions)
    if st.button("Finish & Exit"):
        st.session_state.step = "exit"
        st.rerun()

# STEP 4: EXIT (Mandatory Assignment Requirement)
elif st.session_state.step == "exit":
    st.success("✅ Application Submitted Successfully!")
    st.balloons()
    st.write(f"Thank you, {st.session_state.candidate_data['name']}. Our team will review your profile.")
    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()
