import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import base64

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

# --- PDF GENERATOR FUNCTION ---
def create_pdf(lesson_text, subject, age, location):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="The Pocket School | Lesson Plan", ln=True, align='C')
    
    # Metadata
    pdf.set_font("Arial", "I", 12)
    pdf.cell(200, 10, txt=f"Subject: {subject} | Age: {age} | Location: {location}", ln=True, align='C')
    pdf.ln(10)
    
    # Body Content
    pdf.set_font("Arial", size=12)
    
    # Clean up text (FPDF doesn't like markdown asterisks or emojis)
    clean_text = lesson_text.replace("**", "").replace("#", "")
    
    # Handle encoding (replace emojis with ? to prevent crashing)
    clean_text = clean_text.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(0, 10, clean_text)
    
    return pdf.output(dest='S').encode('latin-1')

# --- UI LAYOUT ---
st.title("🌍 The Pocket School")
st.markdown("**Powered by Rhythm Logic AI**")

col1, col2 = st.columns(2)
with col1:
    student_age = st.selectbox("Student Age", ["6-8 Years", "9-11 Years", "12-14 Years", "15+ Years"])
with col2:
    subject = st.selectbox("Subject", ["Mathematics", "Science", "English/Reading", "Social Studies", "Business"])

region = st.text_input("📍 Region:", "Lagos, Nigeria")
topic_drill = st.text_input("Specific Topic:", placeholder="e.g. Fractions")

# --- THE ENGINE ---
def generate_lesson_google(age, subj, loc, topic):
    
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
    - The Quiz (10 Questions)
    """

    user_request = f"Create a lesson for age {age} on {subj} about {topic} in {loc}."
    full_prompt = f"{system_instruction}\n\nTASK: {user_request}"
    
    # Using the Lite model that works for you
    model = genai.GenerativeModel('gemini-2.0-flash-lite-001')
    
    response = model.generate_content(full_prompt)
    return response.text

# --- MAIN ACTION ---
if "lesson_content" not in st.session_state:
    st.session_state.lesson_content = ""

if st.button("🎓 Start Class"):
    try:
        with st.spinner("Teacher is preparing..."):
            # Generate and store in session state so it doesn't disappear when we click download
            st.session_state.lesson_content = generate_lesson_google(student_age, subject, region, topic_drill)
            st.session_state.generated = True
            
    except Exception as e:
        st.error(f"Error: {e}")

# Display Result if it exists
if st.session_state.lesson_content:
    st.success("Class is in session!")
    st.markdown(f"<div class='lesson-box'>{st.session_state.lesson_content}</div>", unsafe_allow_html=True)
    
    # --- DOWNLOAD BUTTON ---
    pdf_bytes = create_pdf(st.session_state.lesson_content, subject, student_age, region)
    
    st.download_button(
        label="📥 Download Lesson Plan (PDF)",
        data=pdf_bytes,
        file_name="pocket_school_lesson.pdf",
        mime="application/pdf"
    )