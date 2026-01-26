import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions
import io
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Rhythm Logic GPS", page_icon="🧭", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton button { width: 100%; border-radius: 12px; font-weight: bold; background-color: #d4af37; color: black; border: none; padding: 15px 0px; }
    .stButton button:hover { background-color: #f4cf57; color: black; }
    h1, h2 { color: #d4af37; text-align: center; font-family: 'Helvetica', sans-serif; text-transform: uppercase; letter-spacing: 2px; }
    .step-text { text-align: center; font-size: 18px; margin-bottom: 20px; color: #ccc; }
    .stDeployButton {display:none;}
    /* Highlight the Strategy Section */
    .strategy-box { border: 1px solid #d4af37; padding: 10px; border-radius: 10px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if "step" not in st.session_state: st.session_state.step = 1
if "project_type" not in st.session_state: st.session_state.project_type = "Book Chapter"
if "work_style" not in st.session_state: st.session_state.work_style = "Teamwork"
if "last_draft" not in st.session_state: st.session_state.last_draft = ""

# --- 3. SECURITY ---
api_key = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except:
    pass

if not api_key:
    st.warning("🔒 Security Check")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    if not api_key: st.stop()

# --- 4. THE ANTI-CRASH ENGINE ---

def retry_generation(model, contents):
    """
    Tries to generate content. If we hit a Rate Limit (ResourceExhausted),
    it waits 4 seconds and tries again.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(contents)
            return response.text
        except exceptions.ResourceExhausted:
            time.sleep(4) # Wait for the quota to reset
            continue
        except Exception as e:
            return f"Error: {e}"
    return "⚠️ High Traffic: Google is busy. Please wait a minute and try again."

def run_rhythm_logic(audio_file, mode, style, key, current_draft=""):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # THE MANDATORY STRATEGY INSTRUCTION
    strategy_mandate = """
    CRITICAL OUTPUT RULE:
    You must END your response with a section called "🔮 RHYTHM LOGIC STRATEGY".
    In this section, you must ask the user 3 specific, strategic questions about what to do next.
    
    Examples of questions you should ask:
    - "Do you want to expand this into a full verse?"
    - "Should we change the tone to be more aggressive?"
    - "Do you need help rhyming the next line?"
    
    NEVER output just the text. ALWAYS output the text + the questions.
    """

    # 1. HANDLING UPDATES
    if current_draft:
        prompt = f"""
        You are an expert Editor.
        1. UPDATE the draft below based on the user's audio instructions.
        2. Keep the goal of writing a {mode} in mind.
        
        CURRENT DRAFT:
        {current_draft}
        
        {strategy_mandate}
        """
        content_payload = [prompt, {"mime_type": "audio/mp3", "data": audio_file.read()}]
    
    # 2. HANDLING NEW CREATION
    else:
        if style == "✨ Spark Me (Inspiration)":
            prompt = f"""
            You are a Creative Muse. The user has an idea for a {mode}.
            1. Transcribe the idea.
            2. Propose 3 distinct directions they could take.
            {strategy_mandate}
            """
        
        elif style == "🤝 Co-Pilot (Teamwork)":
            prompt = f"""
            You are a Ghostwriter. We are writing a {mode}.
            1. Transcribe the audio.
            2. Write a polished Draft Version 1.0 based on it.
            {strategy_mandate}
            """
            
        elif style == "🎓 Solo (Advice Only)":
            prompt = f"""
            You are a Coach. The user is practicing a {mode}.
            1. Transcribe exactly what they performed.
            2. Give a critique (Strengths/Weaknesses).
            {strategy_mandate}
            """
        content_payload = [prompt, {"mime_type": "audio/mp3", "data": audio_file.read()}]

    # USE THE RETRY FUNCTION
    return retry_generation(model, content_payload)

def text_chat(text_input, current_draft, key):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    Update the draft below based on this request: "{text_input}"
    
    CRITICAL: After updating the text, add a "🔮 RHYTHM LOGIC STRATEGY" section with 3 questions on what to do next.
    
    DRAFT:
    {current_draft}
    """
    
    # USE THE RETRY FUNCTION
    return retry_generation(model, prompt)

# --- 5. THE APP FLOW ---

st.title("RHYTHM LOGIC GPS")

# SIDEBAR RESET
with st.sidebar:
    st.write(f"**Project:** {st.session_state.project_type}")
    if st.button("🔄 Start New Project"):
        st.session_state.step = 1
        st.session_state.last_draft = ""
        st.rerun()

# STEP 1: PROJECT TYPE
if st.session_state.step == 1:
    st.write("")
    st.markdown("## 1. What can I help you write today?")
    st.write("")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        project = st.selectbox(
            "Select Project Type",
            ["Book Chapter", "Song Lyrics", "Sci-Fi Scene", "Blog Post", "Business Proposal", "Speech / Talk", "Personal Journal"],
            label_visibility="collapsed"
        )
        st.write("")
        if st.button("Next ➡"):
            st.session_state.project_type = project
            st.session_state.step = 2
            st.rerun()

# STEP 2: WORKFLOW
elif st.session_state.step == 2:
    st.markdown(f"## 2. Project: **{st.session_state.project_type}**")
    st.markdown("<p class='step-text'>Choose your Ghostwriter Mode:</p>", unsafe_allow_html=True)
    
    style = st.radio(
        "Workflow:",
        ["✨ Spark Me (Inspiration)", "🤝 Co-Pilot (Teamwork)", "🎓 Solo (Advice Only)"],
        captions=[
            "I'll listen to your idea and give you 3 creative paths + strategy questions.",
            "We write together. You talk, I write the draft + ask what's next.",
            "I critique your performance without changing your words + ask guidance questions."
        ]
    )
    
    st.write("")
    if st.button("Enter Studio 🚀"):
        st.session_state.work_style = style
        st.session_state.step = 3
        st.rerun()

# STEP 3: STUDIO
elif st.session_state.step == 3:
    st.markdown(f"### 🎙️ {st.session_state.project_type} Studio")
    st.caption(f"Mode: {st.session_state.work_style}")
    st.divider()

    # INPUTS
    tab1, tab2 = st.tabs(["🔴 Record", "📂 Upload"])
    audio_data = None
    with tab1:
        audio_rec = st.audio_input("Record Audio")
        if audio_rec: audio_data = audio_rec
    with tab2:
        audio_up = st.file_uploader("Upload File", type=['mp3','wav','m4a'])
        if audio_up: audio_data = audio_up

    # RUN
    if audio_data:
        if st.button("⚡ Run Rhythm Logic"):
            with st.spinner("Analyzing & Strategizing..."):
                result = run_rhythm_logic(audio_data, st.session_state.project_type, st.session_state.work_style, api_key, st.session_state.last_draft)
                st.session_state.last_draft = result
                st.rerun()

    # OUTPUT
    if st.session_state.last_draft:
        st.success("Analysis Complete")
        
        # EDITOR
        new_text = st.text_area("Workspace", st.session_state.last_draft, height=500)
        st.session_state.last_draft = new_text
        
        # DOWNLOAD
        st.download_button("💾 Save Text", st.session_state.last_draft, "RL_Draft.txt")
        
        # CHAT
        st.divider()
        st.markdown("#### 🎬 Director's Chair")
        st.caption("Tell the AI what to do next (e.g., 'Answer Question 1' or 'Make it funnier')")
        
        user_instruct = st.text_input("Instruction:", label_visibility="collapsed", placeholder="Type your next instruction here...")
        
        if st.button("Update Draft"):
            if user_instruct:
                with st.spinner("Updating... (If this takes a moment, we are bypassing traffic)"):
                    updated = text_chat(user_instruct, st.session_state.last_draft, api_key)
                    st.session_state.last_draft = updated
                    st.rerun()