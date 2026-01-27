import streamlit as st
from openai import OpenAI
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
# We look for OPENROUTER_API_KEY in secrets
if "OPENROUTER_API_KEY" in st.secrets:
    api_key = st.secrets["OPENROUTER_API_KEY"]
else:
    st.error("🔑 Critical Error: OPENROUTER_API_KEY missing from secrets.")
    st.stop()

# --- THE "SAFE" MODEL LIST (OpenRouter IDs) ---
# This list tries FREE Google models first, then cheap ones.
MODEL_CASCADE = [
    "google/gemini-2.0-flash-exp:free",      # Priority 1: Smart & Free
    "google/gemini-2.0-flash-lite-preview-02-05:free", # Priority 2: Fast & Free
    "google/gemini-flash-1.5",               # Priority 3: Cheap Paid (Backup)
    "meta-llama/llama-3-8b-instruct:free",   # Priority 4: Non-Google Backup (Free)
]

# --- UI LAYOUT ---
st.title("🌍 The Pocket School")
st.markdown("**Universal Education Engine.** Powered by OpenRouter.")

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
    
    for model_name in MODEL_CASCADE:
        try:
            # Update UI status
            status_placeholder.markdown(f"<span class='status-badge'>📡 Contacting: {model_name}...</span>", unsafe_allow_html=True)
            
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
            
            # If successful, return text and model name
            return completion.choices[0].message.content, model_name
            
        except Exception as e:
            # If it fails (429 or other), print error and try next model
            print(f"⚠️ Model {model_name} failed: {e}")
            last_error = e
            continue 
            
    # If ALL models fail
    raise last_error

# --- MAIN ACTION ---
status_placeholder = st.empty()

if st.button("🎓 Generate Lesson"):
    try:
        with st.spinner("Preparing class materials..."):
            lesson_content, successful_model = generate_lesson_cascade(api_key, student_age, subject, region, topic_drill)
        
        # Success
        status_placeholder.empty()
        st.success(f"Class is in session! (Teacher: {successful_model})")
        st.markdown(f"<div class='lesson-box'>{lesson_content}</div>", unsafe_allow_html=True)
        
    except Exception as e:
        status_placeholder.empty()
        st.error(f"School is temporarily closed. All satellites busy. ({e})")