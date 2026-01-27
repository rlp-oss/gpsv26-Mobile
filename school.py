import streamlit as st
from openai import OpenAI
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="The Pocket School", page_icon="🌍", layout="centered")

# --- CUSTOM STYLING (Low Data / High Contrast) ---
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
    .info-text { font-size: 12px; color: #666; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: SETTINGS ---
with st.sidebar:
    st.header("⚙️ School Settings")
    
    # Get API Key from Secrets or User Input
    try:
        api_key = st.secrets["OPENROUTER_API_KEY"]
    except:
        api_key = st.text_input("Enter OpenRouter API Key:", type="password")
        
    st.markdown("---")
    # Dropdown to choose model (OpenRouter gives you choices)
    model_choice = st.selectbox(
        "Select AI Teacher:", 
        ["google/gemini-2.0-flash-exp:free", "meta-llama/llama-3-8b-instruct:free", "mistralai/mistral-7b-instruct:free"],
        index=0
    )
    
    st.info("ℹ️ **Note:** These models are currently FREE via OpenRouter.")

# --- MAIN INTERFACE ---
st.title("🌍 The Pocket School")
st.markdown("**Universal Education Engine.** Type your region, pick a subject, and get a lesson plan tailored to your culture.")

# --- INPUTS ---
col1, col2 = st.columns(2)
with col1:
    student_age = st.selectbox("Student Age", ["6-8 Years (Primary)", "9-11 Years (Middle)", "12-14 Years (Junior Secondary)", "15+ Years (Senior)"])
with col2:
    subject = st.selectbox("Subject", ["Mathematics", "Science", "English/Reading", "Social Studies", "History", "Business/Trade"])

region = st.text_input("📍 Local Region (Crucial for Context):", "Lagos, Nigeria", help="Enter the city or country. The AI will use local currency, names, and geography.")
topic_drill = st.text_input("Specific Topic (Optional):", placeholder="e.g. Photosynthesis, Fractions, The Civil War")

# --- AI GENERATION LOGIC ---
def generate_lesson(key, model, age, subj, loc, topic):
    
    # Configure OpenRouter Client
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=key,
    )
    
    # The Prompt: Forces the AI to be a "Local Teacher"
    prompt = f"""
    Act as an expert primary/secondary school teacher located in {loc}.
    Create a detailed, culturally relevant lesson plan for a student aged {age} about {subj}.
    
    SPECIFIC TOPIC: {topic if topic else "Choose a fundamental topic for this age group"}
    
    CRITICAL RULES:
    1. **Context is King:** You MUST use local names (e.g., if in Nigeria, use Emeka or Chioma), local currency (e.g., Naira), local foods (e.g., Jollof, Yams), and local geography.
    2. **No Western Default:** Do not use dollars, apples, or snow unless relevant to {loc}.
    3. **Tone:** Encouraging, clear, and authoritative but kind.
    4. **Structure:**
       - **Topic Title** (Bold)
       - **The 2-Minute Lesson:** A clear explanation of the concept using simple language.
       - **Real-World Example:** Explain the concept using a daily life scenario in {loc}.
       - **Interactive Activity:** Something the student can do right now without buying supplies (e.g., "Go outside and count the red cars").
       - **Pop Quiz:** 3 Questions to test understanding.
    """
    
    with st.spinner(f"👩‍🏫 Teacher is writing the lesson plan for {loc}..."):
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful, culturally aware local teacher."},
                {"role": "user", "content": prompt}
            ],
            # OpenRouter required headers
            extra_headers={
                "HTTP-Referer": "https://rhythm-logic.com", 
                "X-Title": "The Pocket School",
            },
        )
        return completion.choices[0].message.content

# --- THE TRIGGER ---
if st.button("🎓 Generate Lesson Plan"):
    if not api_key:
        st.error("Please provide an OpenRouter API Key in the sidebar.")
        st.stop()
        
    try:
        lesson_output = generate_lesson(api_key, model_choice, student_age, subject, region, topic_drill)
        
        # Display Result
        st.markdown(f"<div class='lesson-box'>{lesson_output}</div>", unsafe_allow_html=True)
        
        # Save/Export Option
        st.download_button("💾 Download Lesson (Text)", lesson_output, file_name="Lesson_Plan.txt")
        
    except Exception as e:
        st.error(f"Class cancelled. Error: {e}")

# --- FOOTER ---
st.divider()
st.markdown("<p style='text-align: center; class: info-text;'>Built with ❤️ by Rhythm Logic for the world.</p>", unsafe_allow_html=True)