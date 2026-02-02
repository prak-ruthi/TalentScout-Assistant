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
    st.session_state.step = "greeting"  # Start with Greeting as per assignment
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {}
if "questions" not in st.session_state:
    st.session_state.questions = None

# --- LLM FUNCTION ---
def generate_questions(tech, exp, pos, api_key):
    try:
        genai.configure(api_key=api_key)
        # Using the standard stable model for maximum compatibility
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Act as a senior technical recruiter. 
        Generate 3 challenging interview questions for a candidate applying for the '{pos}' position.
        The candidate has {exp} years experience in: {tech}. 
        Focus on real-world architecture, system design, and debugging.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- MAIN UI LOGIC ---
st.title("🤖 TalentScout Hiring Assistant")

# Safety Gate
if not user_api_key:
    st.warning("Please enter your API Key in the sidebar to begin.")
    st.stop()

# --- STEP 1: GREETING SCREEN (MANDATORY REQUIREMENT) ---
if st.session_state.step == "greeting":
    st.subheader("Welcome to TalentScout")
    st.write("""
    I am your AI-powered Technical Recruitment Assistant. My goal is to streamline the 
    initial screening process by gathering candidate details and generating specialized 
    technical assessments.
    
    **How it works:**
    1. Provide your professional details.
    2. I analyze your tech stack and experience.
    3. I generate custom, high-level technical questions for your interview.
    """)
    if st.button("Start Application"):
        st.session_state.step = "info_gathering"
        st.rerun()

# --- STEP 2: INFO GATHERING (ALL MANDATORY FIELDS ADDED) ---
elif st.session_state.step == "info_gathering":
    with st.form("info_form"):
        st.subheader("Candidate Information")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            phone = st.text_input("Phone Number")
        with col2:
            position = st.text_input("Desired Position(s)")
            location = st.text_input("Current Location")
            exp = st.number_input("Years of Experience", min_value=0, max_value=50, step=1)
        
        tech = st.text_area("Tech Stack (e.g., Python, AWS, React, SQL)")
        
        submitted = st.form_submit_button("Generate Assessment")
        
        if submitted:
            # Validate all fields are filled
            if all([name, email, phone, position, location, tech]):
                st.session_state.candidate_data = {
                    "name": name, 
                    "tech": tech, 
                    "exp": exp,
                    "position": position
                }
                st.session_state.step = "view_questions"
                st.rerun()
            else:
                st.error("All fields are mandatory. Please fill in missing details.")

# --- STEP 3: TECHNICAL SCREENING ---
elif st.session_state.step == "view_questions":
    data = st.session_state.candidate_data
    st.subheader(f"Technical Screening: {data['name']}")
    st.caption(f"Role: {data['position']} | Experience: {data['exp']} Years")
    
    if st.session_state.questions is None:
        with st.spinner("Analyzing profile and generating questions..."):
            result = generate_questions(data['tech'], data['exp'], data['position'], user_api_key)
            st.session_state.questions = result
            st.rerun()

    st.markdown("---")
    st.markdown(st.session_state.questions)
    st.markdown("---")
    
    if st.button("Finish & Exit"):
        st.session_state.step = "exit"
        st.rerun()

# --- STEP 4: EXIT SCREEN (MANDATORY REQUIREMENT) ---
elif st.session_state.step == "exit":
    st.success("✅ Application Submitted Successfully!")
    st.balloons()
    st.write(f"Thank you for applying, **{st.session_state.candidate_data['name']}**.")
    st.write("The TalentScout team will review your responses and contact you via the provided email/phone.")
    
    if st.button("Start New Screening"):
        st.session_state.clear()
        st.rerun()
