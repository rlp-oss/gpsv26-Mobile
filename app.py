import warnings
warnings.filterwarnings("ignore")

import streamlit as st
from openai import OpenAI # <--- We switched libraries
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="RL GPS v26 Mobile", page_icon="🧭", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton button { width: 100%; border-radius: 12px; font-weight: bold; background-color: #d4af37; color: black; border: none; padding: 15px 0px; }
    .stButton button:hover { background-color: #f4cf57; color: black; }
    h1, h2 { color: #d4af37; text-align: center; font-family: 'Helvetica', sans-serif; text-transform: uppercase; letter-spacing: 2px; }
    .step-text { text-align: center; font-size: 18px; margin-bottom: 20px; color: #ccc; }
    .stDeployButton {display:none;}
    .director-box { border: 1px solid #444; padding: 20px; border-radius: 15px; background-color: #1e1e1e; margin-top: 20px;}
    
    /* Gumroad Paywall Styles */
    .paywall-box { border: 2px solid #ff90e8; padding: 30px; border-radius: 20px; text-align: center; background-color: #1a1a1a; margin-top: 50px; }
    .price-tag { font-size: 40px; color: #d4af37; font-weight: bold; }
    .per-month { font-size: 16px; color: #aaa; }
</style>
""", unsafe_allow_html=True)

# --- 2. BUSINESS CONFIGURATION ---
GUMROAD_LINK = "https://rhythmlogic.gumroad.com/l/dldqoy" 
ACCESS_CODE = "RHYTHM2026" 

# --- 3. SESSION STATE ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "step" not in st.session_state: st.session_state.step = 1
if "project_type" not in st.session_state: st.session_state.project_type = "Book Chapter"
if "work_style" not in st.session_state: st.session_state.work_style = "Teamwork"
if "last_draft" not in st.session_state: st.session_state.last_draft = ""

# --- 4. THE PAYWALL ---
if not st.session_state.authenticated:
    st.title("RL GPS v26")
    st.markdown(f"""
    <div class='paywall-box'>
        <h2>Pro Access Required</h2>
        <p>Unlock the full AI studio.</p>
        <div class='price-tag'>$20<span class='per-month'>/mo</span></div>
        <br>
        <a href="{GUMROAD_LINK}" target="_blank">
            <button style="background-color: #ff90e8; color: black; font-weight: bold; padding: 15px 32px; border: none; border-radius: 10px; cursor: pointer; width: 100%; font-size: 18px;">
                👉 JOIN ON GUMROAD
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    code_input = st.text_input("Enter Access Code:", type="password")
    if st.button("Unlock Studio 🔓"):
        if code_input == ACCESS_CODE:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid Code.")
    st.stop()

# =========================================================
# THE OPENROUTER AI ENGINE
# =========================================================

# --- SECURITY ---
api_key = None
try:
    if "OPENROUTER_API_KEY" in st.secrets:
        api_key = st.secrets["OPENROUTER_API_KEY"]
except:
    pass
if not api_key:
    st.warning("🔒 OpenRouter Key Required")
    api_key = st.text_input("Enter OpenRouter Key (sk-or-v1...):", type="password")
    if not api_key: st.stop()

def run_openrouter(audio_file, mode, style, key, current_draft="", instruction=""):
    # Connect to OpenRouter
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=key,
    )
    
    # Transcription (Mockup for simplicity or use Whisper if available)
    # Since OpenRouter is text-first, we will treat audio as a prompt trigger for now
    # Or if your audio input is text-based instructions
    # Note: For true audio-to-text, we usually need Whisper. 
    # For now, let's assume the user is typing or we use a basic speech-to-text widget if available.
    
    # STRATEGY MANDATE
    strategy_mandate = """
    CRITICAL RULE: End response with '🔮 RHYTHM LOGIC STRATEGY': 3 short strategic questions for the user.
    """

    if current_draft:
        # EDIT MODE
        system_msg = "You are an expert Editor."
        user_msg = f"Update this draft based on: {instruction}\n\nDRAFT:\n{current_draft}\n\n{strategy_mandate}"
    else:
        # CREATION MODE
        system_msg = f"You are a Creative Partner. Goal: Write a {mode}. Style: {style}."
        # If audio_file was passed, we would need to transcribe it first.
        # Since we are switching APIs, let's prompt the user for TEXT context if audio fails
        user_msg = f"Start the {mode}. {strategy_mandate}"

    # CALL THE MODEL (Using Google Gemini Pro via OpenRouter)
    try:
        completion = client.chat.completions.create(
            model="google/gemini-2.0-flash-001", # <--- Using Gemini via OpenRouter
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# --- APP FLOW ---
with st.sidebar:
    st.success("✅ **Connected**")
    if st.button("Log Out"):
        st.session_state.authenticated = False
        st.rerun()

if st.session_state.step == 1:
    st.title("RL GPS v26")
    st.write("## 1. What are we writing?")
    project = st.selectbox("Project Type", ["Book Chapter", "Song Lyrics", "Blog Post"], label_visibility="collapsed")
    if st.button("Next ➡"):
        st.session_state.project_type = project
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 2:
    st.title("RL GPS v26")
    st.write(f"## 2. Mode: {st.session_state.project_type}")
    style = st.radio("Style:", ["✨ Spark Me", "🤝 Co-Pilot", "🎓 Solo"])
    if st.button("Enter Studio 🚀"):
        st.session_state.work_style = style
        st.session_state.step = 3
        st.rerun()

elif st.session_state.step == 3:
    st.markdown(f"### 🎙️ {st.session_state.project_type} Studio")
    
    # Input Area
    if not st.session_state.last_draft:
        user_input = st.text_area("What is your idea? (Dictate or Type)", height=150)
        if st.button("⚡ Run Rhythm Logic"):
             with st.spinner("Connecting to OpenRouter..."):
                # Pass the text as the 'instruction' since we removed direct audio processing for stability
                result = run_openrouter(None, st.session_state.project_type, st.session_state.work_style, api_key, current_draft="", instruction=user_input)
                st.session_state.last_draft = result
                st.rerun()

    if st.session_state.last_draft:
        st.success("Draft Generated")
        st.text_area("Workspace", st.session_state.last_draft, height=400)
        
        st.markdown("#### 🎬 Director's Chair")
        refine = st.text_input("Instructions (e.g., 'Make it darker')")
        if st.button("Update Draft"):
             with st.spinner("Refining..."):
                result = run_openrouter(None, st.session_state.project_type, st.session_state.work_style, api_key, current_draft=st.session_state.last_draft, instruction=refine)
                st.session_state.last_draft = result
                st.rerun()