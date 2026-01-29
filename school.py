import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="The Pocket School", page_icon="🌍", layout="centered")

# --- CUSTOM STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #fcfcfc; color: #111; }
    h1 { color: #2e7d32; font-family: 'Arial', sans-serif; letter-spacing: -1px; }
    .lesson-box { 
        background-color: #f1f8e9; 
        padding: 25px; 
        border-radius: 12px; 
        border-left: 6px solid #2e7d32;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
    .stButton button { width: 100%; background-color: #2e7d32; color: white; font-weight: bold; padding: 12px; }
    .stButton button:hover { background-color: #1b5e20; }
</style>
""", unsafe_allow_html=True)

# --- CREDENTIALS ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("🔑 Critical Error: GEMINI_API_KEY missing from secrets.")
    st.stop()

# --- UI LAYOUT ---
st.title("🌍 The Pocket School")
st.markdown("**Universal Education Engine**")

col1, col2 = st.columns(2)
with col1:
    student_age = st.selectbox("Student Age", ["6-8 Years", "9-11 Years", "12-14 Years", "15+ Years"])
with col2:
    subject = st.selectbox("Subject", ["Mathematics", "Science", "English/Reading", "Social Studies", "Business"])

region = st.text_input("📍 Region:", "Lagos, Nigeria")
topic_drill = st.text_input("Specific Topic:", placeholder="e.g. Fractions")

# --- THE ENGINE ---
def generate_lesson_google(age, subj, loc, topic):
    
    # 1. THE BRAIN (Your Gem Instructions)
    # We paste the text here so the App knows how to behave.
    system_instruction = """
    Role: You are the "Universal Education Engine," a highly adaptive, localized teacher.
    Directive: Adapt every lesson to the user's specific Location (City/Country). Use local names, currency, and culture.
    Constraints: 
    1. Zero-Cost: No supplies allowed. 
    2. Format: Text-only, structured.
    
    Structure:
    - The Hook (Connect to daily life in the city)
    - The Concept (Simple explanation)
    - Real-World Example (Use a local example)
    - The Activity (No supplies needed)
    - The Quiz (3 Questions)
    """

    # 2. THE USER REQUEST
    user_request = f"Create a lesson for age {age} on {subj} about {topic} in {loc}."

    # 3. GENERATE
    full_prompt = f"{system_instruction}\n\nTASK: {user_request}"
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(full_prompt)
    return response.text

# --- MAIN ACTION ---
if st.button("🎓 Start Class"):
    try:
        with st.spinner("Teacher is preparing..."):
            lesson_content = generate_lesson_google(student_age, subject, region, topic_drill)
        
        st.success("Class is in session!")
        st.markdown(f"<div class='lesson-box'>{lesson_content}</div>", unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error: {e}")