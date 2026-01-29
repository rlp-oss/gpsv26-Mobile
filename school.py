import streamlit as st
from openai import OpenAI
import google.generativeai as genai # <--- REQUIRED: Install 'google-generativeai'
import time

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
    .status-badge {
        font-size: 12px;
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 4px 8px;
        border-radius: 4px;
        border: 1px solid #c8e6c9;
        margin-bottom: 10px;
        display: inline-block;
    }
    .stButton button { width: 100%; background-color: #2e7d32; color: white; font-weight: bold; padding: 12px; }
    .stButton button:hover { background-color: #1b5e20; }
</style>
""", unsafe_allow_html=True)

# --- SETUP CREDENTIALS ---
# 1. OpenRouter (Primary Layer)
if "OPENROUTER_API_KEY" in st.secrets:
    openrouter_key = st.secrets["OPENROUTER_API_KEY"]
else:
    st.error("🔑 Critical Error: OPENROUTER_API_KEY missing from secrets.")
    st.stop()

# 2. Google Gemini (Backup Layer - Direct)
gemini_backup_ready = False
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    gemini_backup_ready = True

# --- THE MODEL LIST (OpenRouter IDs) ---
# Removed the broken Llama :free tag and prioritized stable Google models
MODEL_CASCADE = [
    "google/gemini-2.0-flash-lite-preview-02-05:free", # Fast & New
    "google/gemini-flash-1.5-8b",                      # Very Cheap/Fast
    "mistralai/mistral-7b-instruct:free",              # Reliable Free Alternative
]

# --- UI LAYOUT ---
st.title("🌍 The Pocket School")
st.markdown("**Universal Education Engine.**")

col1, col2 = st.columns(2)
with col1:
    student_age = st.selectbox("Student Age", ["6-8 Years", "9-11 Years", "12-14 Years", "15+ Years"])
with col2:
    subject = st.selectbox("Subject", ["Mathematics", "Science", "English/Reading", "Social Studies", "Business"])

region = st.text_input("📍 Region:", "Lagos, Nigeria", help="Enter city/country. The AI adapts the lesson to this location.")
topic_drill = st.text_input("Specific Topic (Optional):", placeholder="e.g. Fractions, Photosynthesis")

# --- ROBUST GENERATION FUNCTION ---
def generate_lesson_cascade(key, age, subj, loc, topic):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=key,
    )

    prompt = f"""
    Act as an expert teacher in {loc}. Create a lesson plan for age {age} on {subj}.
    TOPIC: {topic if topic else "Fundamental Concept"}
    
    RULES:
    1. Use local names, currency, food, and places from {loc}.
    2. NO supplies needed. Text only.
    3. Structure: 
       - **Topic**
       - **Concept (2 mins)**
       - **Real Life Example (in {loc})**
       - **Activity (No supplies)**
       - **Quiz (3 Questions)**
    """

    last_error = None
    
    # --- LAYER 1: OpenRouter Cascade ---
    for model_name in MODEL_CASCADE:
        try:
            status_placeholder.markdown(f"<span class='status-badge'>📡 Calling Teacher: {model_name}...</span>", unsafe_allow_html=True)
            
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful local teacher."},
                    {"role": "user", "content": prompt}
                ],
                extra_headers={
                    "HTTP-Referer": "https://rhythm-logic.com", 
                    "X-Title": "The Pocket School",
                },
            )
            return completion.choices[0].message.content, model_name
            
        except Exception as e:
            print(f"⚠️ {model_name} failed: {e}")
            last_error = e
            continue 
            
    # --- LAYER 2: Direct Google Backup (The Safety Net) ---
    if gemini_backup_ready:
        try:
            status_placeholder.markdown(f"<span class='status-badge'>🛡️ OpenRouter Busy. Switching to Direct Satellite (Gemini)...</span>", unsafe_allow_html=True)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text, "Google Gemini (Direct Backup)"
        except Exception as google_e:
            print(f"Google Backup failed: {google_e}")
            
    # If EVERYTHING fails
    raise last_error

# --- MAIN ACTION ---
status_placeholder = st.empty()

if st.button("🎓 Generate Lesson"):
    try:
        with st.spinner("Preparing class materials..."):
            lesson_content, successful_model = generate_lesson_cascade(openrouter_key, student_age, subject, region, topic_drill)
        
        # Success
        status_placeholder.empty()
        st.success(f"Class is in session! (Teacher: {successful_model})")
        st.markdown(f"<div class='lesson-box'>{lesson_content}</div>", unsafe_allow_html=True)
        
    except Exception as e:
        status_placeholder.empty()
        st.error(f"School is temporarily closed. All satellites busy. ({e})")