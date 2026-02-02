import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖", layout="centered")

# --- SIDEBAR: SECURE KEY INPUT ---
with st.sidebar:
    st.title("🔑 API Settings")
    user_api_key = st.text_input("Enter Gemini API Key", type="password", help="Get a key from ai.google.dev")
    
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()
    
    st.markdown("---")
    st.info("Powered by Gemini for intelligent technical screening.")

# --- SESSION STATE INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state.step = "greeting"  # Start with mandatory Greeting 
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {}
if "questions" not in st.session_state:
    st.session_state.questions = None

# --- LLM FUNCTION ---
def generate_questions(tech, exp, pos, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Act as a senior technical recruiter for TalentScout. 
        The candidate is applying for the position of '{pos}' with {exp} years of experience.
        Their tech stack includes: {tech}.
        Generate 3-5 challenging technical questions tailored to assess their proficiency in these specific technologies.
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

# --- STEP 1: GREETING & OVERVIEW  ---
if st.session_state.step == "greeting":
    st.subheader("Hello! I am your TalentScout Assistant.")
    st.write("""
    I'm here to help you with the initial screening process for our technology placements.
    I will gather some basic information from you and then generate a set of technical 
    questions based on your specific tech stack to assess your proficiency.
    """)
    if st.button("Start Screening"):
        st.session_state.step = "info_gathering"
        st.rerun()

# --- STEP 2: INFORMATION GATHERING  ---
elif st.session_state.step == "info_gathering":
    with st.form("info_form"):
        st.subheader("Candidate Information")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            phone = st.text_input("Phone Number")
        with col2:
            exp = st.number_input("Years of Experience", min_value=0, max_value=50, step=1)
            pos = st.text_input("Desired Position(s)")
            loc = st.text_input("Current Location")
        
        tech = st.text_area("Tech Stack (Languages, Frameworks, Tools, Databases)")
        
        submitted = st.form_submit_button("Generate Assessment")
        
        if submitted:
            # Validate essential fields
            if all([name, email, phone, pos, loc, tech]):
                st.session_state.candidate_data = {
                    "name": name, "email": email, "phone": phone, 
                    "exp": exp, "pos": pos, "loc": loc, "tech": tech
                }
                st.session_state.step = "view_questions"
                st.rerun()
            else:
                st.error("Please fill in all mandatory fields to proceed.")

# --- STEP 3: TECHNICAL QUESTIONS  ---
elif st.session_state.step == "view_questions":
    data = st.session_state.candidate_data
    st.subheader(f"Technical Screening for {data['name']}")
    st.info(f"Targeting: {data['pos']} | Experience: {data['exp']} years")
    
    if st.session_state.questions is None:
        with st.spinner("Generating tailored questions for your tech stack..."):
            result = generate_questions(data['tech'], data['exp'], data['pos'], user_api_key)
            st.session_state.questions = result
            st.rerun()

    st.markdown(st.session_state.questions)
    
    if st.button("Finish & Exit"):
        st.session_state.step = "exit"
        st.rerun()

# --- STEP 4: EXIT & NEXT STEPS  ---
elif st.session_state.step == "exit":
    st.success("Thank you for completing the initial screening!")
    st.write(f"We have recorded your interest in the **{st.session_state.candidate_data['pos']}** position.")
    st.write("Our team will review your profile and the questions generated. We'll be in touch soon via email or phone.")
    
    if st.button("Start New Session"):
        st.session_state.clear()
        st.rerun()
