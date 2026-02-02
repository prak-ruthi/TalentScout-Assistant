import streamlit as st
import google.generativeai as genai

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖", layout="centered")

# --- 2. SIDEBAR: SECURE KEY INPUT ---
with st.sidebar:
    st.title("🔑 API Settings")
    user_api_key = st.text_input("Enter Gemini API Key", type="password", help="Paste your Gemini 1.5 Flash Key")
    
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()
    
    st.markdown("---")
    st.info("Status: **Gemini 1.5 Flash Active**")

# --- 3. SESSION STATE INITIALIZATION ---
# This block prevents the 'KeyError' by ensuring all keys exist from the start
if "step" not in st.session_state:
    st.session_state.step = "greeting"
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {
        "name": "", "email": "", "phone": "", 
        "pos": "", "loc": "", "exp": 0, "tech": ""
    }
if "questions" not in st.session_state:
    st.session_state.questions = None

# --- 4. LLM FUNCTION ---
def generate_questions(tech, exp, pos, api_key):
    try:
        genai.configure(api_key=api_key)
        # Specifically calling 1.5-flash as requested
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Act as a senior technical recruiter for TalentScout. 
        The candidate is applying for '{pos}' with {exp} years of experience.
        Tech stack: {tech}.
        Generate 3-5 challenging technical interview questions that test deep knowledge 
        of architecture and problem-solving.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Connection Error: {str(e)}"

# --- 5. MAIN UI LOGIC ---
st.title("🤖 TalentScout Hiring Assistant")

if not user_api_key:
    st.warning("Please enter your Gemini 1.5 Flash API Key in the sidebar to begin.")
    st.stop()

# STEP 1: GREETING & PURPOSE (Mandatory Requirement)
if st.session_state.step == "greeting":
    st.subheader("Welcome to the TalentScout Technical Screening")
    st.write("""
    I am an agentic AI designed to streamline the recruitment process. 
    I will gather your professional profile and generate a customized technical 
    assessment based on your specific expertise.
    """)
    if st.button("Start Screening"):
        st.session_state.step = "info_gathering"
        st.rerun()

# STEP 2: INFO GATHERING (Mandatory Fields Added)
elif st.session_state.step == "info_gathering":
    with st.form("info_form"):
        st.subheader("Candidate Profile")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            phone = st.text_input("Phone Number")
        with col2:
            pos = st.text_input("Desired Position")
            loc = st.text_input("Current Location")
            exp = st.number_input("Years of Experience", min_value=0, step=1)
        
        tech = st.text_area("Tech Stack (e.g. Python, Django, PostgreSQL, Docker)")
        
        submitted = st.form_submit_button("Generate Assessment")
        if submitted:
            if all([name, email, phone, pos, loc, tech]):
                st.session_state.candidate_data = {
                    "name": name, "email": email, "phone": phone,
                    "pos": pos, "loc": loc, "exp": exp, "tech": tech
                }
                st.session_state.step = "view_questions"
                st.rerun()
            else:
                st.error("Please fill in all mandatory fields to continue.")

# STEP 3: TECHNICAL QUESTIONS
elif st.session_state.step == "view_questions":
    data = st.session_state.candidate_data
    st.subheader(f"Technical Assessment: {data['name']}")
    st.info(f"Targeting: {data['pos']} | {data['exp']} Years Experience")

    if st.session_state.questions is None:
        with st.spinner("Gemini 1.5 Flash is generating your specialized questions..."):
            st.session_state.questions = generate_questions(data['tech'], data['exp'], data['pos'], user_api_key)
            st.rerun()

    st.markdown("---")
    st.markdown(st.session_state.questions)
    st.markdown("---")
    
    if st.button("Finish & Exit"):
        st.session_state.step = "exit"
        st.rerun()

# STEP 4: EXIT (Mandatory Requirement)
elif st.session_state.step == "exit":
    st.success("✅ Application Successfully Processed!")
    st.balloons()
    st.write(f"Thank you, **{st.session_state.candidate_data['name']}**.")
    st.write(f"Your profile for the **{st.session_state.candidate_data['pos']}** role has been recorded.")
    st.info("Our recruitment team will reach out via the provided email or phone number.")
    
    if st.button("Start New Session"):
        st.session_state.clear()
        st.rerun()
