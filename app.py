import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import google.generativeai as genai
import io

# --- 1. SETUP & BRANDING ---
st.set_page_config(page_title="Rhythm Logic GPS", page_icon="🧭", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    /* Gold Buttons */
    .stButton button { width: 100%; border-radius: 12px; font-weight: bold; background-color: #d4af37; color: black; border: none; padding: 15px 0px; }
    .stButton button:hover { background-color: #f4cf57; color: black; }
    /* Headers */
    h1, h2 { color: #d4af37; text-align: center; font-family: 'Helvetica', sans-serif; text-transform: uppercase; letter-spacing: 2px; }
    .step-text { text-align: center; font-size: 18px; margin-bottom: 20px; color: #ccc; }
    .stDeployButton {display:none;}
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

# --- 4. THE PROMPT ENGINE (RE-ENGINEERED) ---
def run_rhythm_logic(audio_file, mode, style, key, current_draft=""):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # ---------------------------------------------------------
    # HERE IS THE FIX: WE FORCE A SPECIFIC OUTPUT STRUCTURE
    # ---------------------------------------------------------
    
    base_instruction = f"""
    You are Rhythm Logic, an expert creative consultant.
    The user is working on a: {mode}.
    
    IMPORTANT: You have TWO jobs.
    1. Transcribe/Process the user's audio.
    2. Generate a STRATEGY SECTION to help them move forward.
    
    NEVER return just the transcription. ALWAYS return the strategy.
    """

    if style == "✨ Spark Me (Inspiration)":
        prompt = f"""
        {base_instruction}
        
        TASK:
        1. Listen to the user's audio idea.
        2. Transcribe it clearly at the top.
        3. Create 3 DISTINCT CREATIVE PATHS they could take with this idea.
        4. Ask 3 "Probing Questions" to help them unlock the next step.
        
        OUTPUT FORMAT:
        **Audio Transcript:**
        (The text)
        
        **⚡ Rhythm Logic Sparks:**
        1. (Idea A)
        2. (Idea B)
        3. (Idea C)
        
        **❓ Strategic Questions:**
        1. (Question)
        2. (Question)
        3. (Question)
        """
    
    elif style == "🤝 Co-Pilot (Teamwork)":
        prompt = f"""
        {base_instruction}
        
        TASK:
        1. Listen to the audio.
        2. Write a POLISHED DRAFT based on the audio (expand it into professional prose/lyrics).
        3. Ask the user what they want to do next.
        
        OUTPUT FORMAT:
        **Draft Version 1.0:**
        (The polished content)
        
        **🚀 Next Steps:**
        (Ask the user: Do they want to expand? Change tone? Add a section?)
        """
        
    elif style == "🎓 Solo (Advice Only)":
        prompt = f"""
        {base_instruction}
        
        TASK:
        1. Transcribe the audio EXACTLY as performed. Do not change a word.
        2. Provide a "Coach's Critique".
        
        OUTPUT FORMAT:
        **Transcript:**
        (Verbatim text)
        
        **🧐 Coach's Notes:**
        * Strengths: ...
        * Weaknesses: ...
        * Recommended Fix: ...
        """
    
    # If refining existing text
    if current_draft:
        prompt = f"""
        UPDATE this draft based on the audio instructions. 
        AFTER updating, ask 2 questions about what to do next.
        
        OLD DRAFT: {current_draft}
        """

    try:
        response = model.generate_content([prompt, {"mime_type": "audio/mp3", "data": audio_file.read()}])
        return response.text
    except Exception as e:
        return f"Error: {e}"

def text_chat(text_input, current_draft, key):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"""
    Update the draft below based on this request: "{text_input}"
    
    After updating, add a "❓ Next Question" section to keep the momentum going.
    
    DRAFT:
    {current_draft}
    """
    return model.generate_content(prompt).text

# --- 5. THE APP FLOW ---

st.title("RHYTHM LOGIC GPS")

# SIDEBAR
with st.sidebar:
    st.write(f"**Project:** {st.session_state.project_type}")
    if st.button("🔄 Start New Project"):
        st.session_state.step = 1
        st.session_state.last_draft = ""
        st.rerun()

# STEP 1: PROJECT TYPE
if st.session_state.step == 1:
    st.write("")
    st.markdown("## 1. What are we building?")
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
            "I'll analyze your idea and give you 3 creative strategies & questions.",
            "We write together. You talk, I write the draft.",
            "I critique your performance without changing your words."
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
        user_instruct = st.text_input("Reply to the AI's questions or give new orders:", placeholder="Ex: Option 2 looks good. Let's write the first verse based on that.")
        if st.button("Update"):
            if user_instruct:
                with st.spinner("Updating..."):
                    updated = text_chat(user_instruct, st.session_state.last_draft, api_key)
                    st.session_state.last_draft = updated
                    st.rerun()