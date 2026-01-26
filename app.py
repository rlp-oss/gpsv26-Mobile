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
    /* Highlight the Director's Chair */
    .director-box { border: 1px solid #444; padding: 20px; border-radius: 15px; background-color: #1e1e1e; margin-top: 20px;}
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if "step" not in st.session_state: st.session_state.step = 1
if "project_type" not in st.session_state: st.session_state.project_type = "Book Chapter"
if "work_style" not in st.session_state: st.session_state.work_style = "Teamwork"
if "last_draft" not in st.session_state: st.session_state.last_draft = ""
# We add a specific key for the refinement text so we can clear it manually
if "refine_text_input" not in st.session_state: st.session_state.refine_text_input = ""

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

# --- 4. THE AI ENGINE ---

def retry_generation(model, contents):
    """Retries generation if we hit a speed limit."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(contents)
            return response.text
        except exceptions.ResourceExhausted:
            time.sleep(4)
            continue
        except Exception as e:
            return f"Error: {e}"
    return "⚠️ Google is busy. Please wait a moment and try again."

def run_rhythm_logic(audio_file, mode, style, key, current_draft=""):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    strategy_mandate = """
    CRITICAL OUTPUT RULE:
    You must END your response with a section called "🔮 RHYTHM LOGIC STRATEGY".
    In this section, ask the user 3 specific, strategic questions about what to do next.
    NEVER output just the text. ALWAYS output the text + the questions.
    """

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
    else:
        # Initial Generation Logic (Same as before)
        base_prompt = f"You are a Creative Partner. We are writing a {mode}. "
        if style == "✨ Spark Me (Inspiration)":
            base_prompt += "Transcribe the audio and propose 3 creative directions."
        elif style == "🤝 Co-Pilot (Teamwork)":
            base_prompt += "Transcribe the audio and write a polished Draft Version 1.0."
        elif style == "🎓 Solo (Advice Only)":
            base_prompt += "Transcribe exactly what was performed and provide a critique."
            
        final_prompt = f"{base_prompt}\n{strategy_mandate}"
        content_payload = [final_prompt, {"mime_type": "audio/mp3", "data": audio_file.read()}]

    return retry_generation(model, content_payload)

def text_refinement(instruction, current_draft, key, is_audio=False):
    """Handles both Text AND Audio instructions for refinement."""
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    base_prompt = f"""
    Update the draft below based on the user's instruction.
    
    CRITICAL: After updating the text, add a "🔮 RHYTHM LOGIC STRATEGY" section.
    
    DRAFT:
    {current_draft}
    """
    
    if is_audio:
        # Instruction is an audio file
        payload = [base_prompt, {"mime_type": "audio/mp3", "data": instruction.read()}]
    else:
        # Instruction is text
        payload = f"{base_prompt}\n\nUSER INSTRUCTION: {instruction}"
    
    return retry_generation(model, payload)

# --- 5. THE APP FLOW ---

st.title("RHYTHM LOGIC GPS")

# SIDEBAR RESET
with st.sidebar:
    st.write(f"**Project:** {st.session_state.project_type}")
    if st.button("🔄 Start New Project"):
        st.session_state.step = 1
        st.session_state.last_draft = ""
        st.session_state.refine_text_input = ""
        st.rerun()

# STEP 1: PROJECT TYPE
if st.session_state.step == 1:
    st.write("")
    st.markdown("## 1. What can I help you write today?")
    st.write("")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        project = st.selectbox("Select Project Type", ["Book Chapter", "Song Lyrics", "Sci-Fi Scene", "Blog Post", "Business Proposal", "Speech", "Journal"], label_visibility="collapsed")
        st.write("")
        if st.button("Next ➡"):
            st.session_state.project_type = project
            st.session_state.step = 2
            st.rerun()

# STEP 2: WORKFLOW
elif st.session_state.step == 2:
    st.markdown(f"## 2. Project: **{st.session_state.project_type}**")
    st.markdown("<p class='step-text'>Choose your Ghostwriter Mode:</p>", unsafe_allow_html=True)
    style = st.radio("Workflow:", ["✨ Spark Me (Inspiration)", "🤝 Co-Pilot (Teamwork)", "🎓 Solo (Advice Only)"])
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

    # INITIAL INPUTS
    if not st.session_state.last_draft:
        tab1, tab2 = st.tabs(["🔴 Record Initial Idea", "📂 Upload File"])
        audio_data = None
        with tab1:
            audio_rec = st.audio_input("Record Audio")
            if audio_rec: audio_data = audio_rec
        with tab2:
            audio_up = st.file_uploader("Upload File", type=['mp3','wav','m4a'])
            if audio_up: audio_data = audio_up

        if audio_data:
            if st.button("⚡ Run Rhythm Logic"):
                with st.spinner("Analyzing..."):
                    result = run_rhythm_logic(audio_data, st.session_state.project_type, st.session_state.work_style, api_key)
                    st.session_state.last_draft = result
                    st.rerun()

    # RESULT & REFINEMENT
    if st.session_state.last_draft:
        # EDITOR
        st.success("Analysis Complete")
        new_text = st.text_area("Workspace", st.session_state.last_draft, height=500)
        st.session_state.last_draft = new_text
        st.download_button("💾 Save Text", st.session_state.last_draft, "RL_Draft.txt")
        
        # --- THE DIRECTOR'S CHAIR (UPGRADED) ---
        st.markdown("<div class='director-box'>", unsafe_allow_html=True)
        st.markdown("#### 🎬 Director's Chair")
        st.caption("Refine your draft using Voice OR Text.")
        
        # 1. VOICE REFINEMENT
        refine_audio = st.audio_input("🎤 Voice Command (e.g., 'Make the dialogue funnier')")
        
        if refine_audio:
            with st.spinner("Listening to your command..."):
                updated = text_refinement(refine_audio, st.session_state.last_draft, api_key, is_audio=True)
                st.session_state.last_draft = updated
                st.rerun()

        st.write("--- OR ---")

        # 2. TEXT REFINEMENT (LARGE BOX + AUTO CLEAR)
        def clear_text():
            """Callback to clear text after submission"""
            st.session_state.refine_text_input = ""

        # We use a form so the 'Clear' logic works smoothly
        with st.form(key='refine_form', clear_on_submit=True):
            user_instruct = st.text_area(
                "Text Instructions:", 
                height=100, 
                placeholder="Type instructions here... (e.g. 'Expand the second paragraph about the dragon')",
                key="widget_refine_input" # Unique key for the widget
            )
            submit_button = st.form_submit_button(label="Update Draft 🔄")
        
        if submit_button and user_instruct:
            with st.spinner("Updating..."):
                updated = text_refinement(user_instruct, st.session_state.last_draft, api_key, is_audio=False)
                st.session_state.last_draft = updated
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)