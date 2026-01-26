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
    /* Hide Deploy Button */
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE MANAGEMENT (The "Brain") ---
# We use this to remember where the user is in the onboarding process
if "step" not in st.session_state:
    st.session_state.step = 1
if "project_type" not in st.session_state:
    st.session_state.project_type = "Book Chapter"
if "work_style" not in st.session_state:
    st.session_state.work_style = "Teamwork"
if "last_draft" not in st.session_state:
    st.session_state.last_draft = ""

# --- 3. SECURITY CHECK ---
api_key = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except:
    pass

if not api_key:
    st.warning("🔒 Security Check")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    if not api_key:
        st.stop()

# --- 4. AI ENGINES (Customized by Mode) ---
def run_rhythm_logic(audio_file, mode, style, key, current_draft=""):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # LOGIC BRANCHING BASED ON USER CHOICE
    if style == "✨ Spark Me (Inspiration)":
        prompt = f"""
        You are a Creative Muse for Rhythm Logic.
        The user wants to write a {mode} but needs inspiration.
        1. Listen to their audio notes (ideas, fragments, vibes).
        2. Transcribe them.
        3. Generate 3 DISTINCT CREATIVE DIRECTIONS or OUTLINES they could take.
        4. Do not write the full piece yet; just pitch the concepts to get them excited.
        """
    
    elif style == "🤝 Co-Pilot (Teamwork)":
        prompt = f"""
        You are an expert Ghostwriter. We are writing a {mode} together.
        1. Listen to the audio.
        2. Transcribe it.
        3. WRITE A FULL DRAFT based on the audio, polishing the prose/lyrics to a professional standard.
        4. At the end, add a "RHYTHM LOGIC STRATEGY" section asking 3 specific questions to help refine the draft.
        """
        
    elif style == "🎓 Solo (Advice Only)":
        prompt = f"""
        You are a tough Editor/Critic. The user is writing a {mode}.
        1. Listen to the audio (which is their draft).
        2. Transcribe it exactly as is.
        3. DO NOT REWRITE IT.
        4. Instead, provide a "CRITICAL ANALYSIS":
           - Strengths
           - Weaknesses
           - 3 Specific Action Steps to improve it.
        """
    
    # If refining existing text
    if current_draft:
        prompt = f"UPDATE the following draft based on the user's audio instructions. Keep the goal of {mode} in mind.\n\nDRAFT:\n{current_draft}"

    try:
        response = model.generate_content([prompt, {"mime_type": "audio/mp3", "data": audio_file.read()}])
        return response.text
    except Exception as e:
        return f"Error: {e}"

def text_chat(text_input, current_draft, key):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"Update this draft based on the request: {text_input}\n\nDRAFT:\n{current_draft}"
    return model.generate_content(prompt).text

# --- 5. THE ONBOARDING FLOW ---

# HEADER
st.title("RHYTHM LOGIC GPS")

# RESET BUTTON (In Sidebar)
with st.sidebar:
    st.write(f"**Current Mode:** {st.session_state.project_type}")
    if st.button("🔄 Start Over"):
        st.session_state.step = 1
        st.session_state.last_draft = ""
        st.rerun()

# --- STEP 1: THE GOAL ---
if st.session_state.step == 1:
    st.write("")
    st.markdown("## 1. What can I help you write today?")
    st.write("")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        project = st.selectbox(
            "Select Project Type",
            [
                "Book Chapter",
                "Song Lyrics",
                "Sci-Fi Scene",
                "Blog Post",
                "Business Proposal",
                "Speech / Talk",
                "Personal Journal"
            ],
            label_visibility="collapsed"
        )
        st.write("")
        if st.button("Next ➡"):
            st.session_state.project_type = project
            st.session_state.step = 2
            st.rerun()

# --- STEP 2: THE VIBE ---
elif st.session_state.step == 2:
    st.markdown(f"## 2. We are writing a **{st.session_state.project_type}**.")
    st.markdown("<p class='step-text'>How would you like to work?</p>", unsafe_allow_html=True)
    
    style = st.radio(
        "Choose your workflow:",
        [
            "✨ Spark Me (Inspiration)", 
            "🤝 Co-Pilot (Teamwork)", 
            "🎓 Solo (Advice Only)"
        ],
        captions=[
            "I'll listen to your messy ideas and give you 3 solid outlines/concepts.",
            "We write together. You talk, I draft the text and polish it.",
            "You write/perform. I listen and critique you like a coach. I won't change your words."
        ]
    )
    
    st.write("")
    if st.button("Enter Studio 🚀"):
        st.session_state.work_style = style
        st.session_state.step = 3
        st.rerun()

# --- STEP 3: THE STUDIO ---
elif st.session_state.step == 3:
    st.markdown(f"### 🎙️ {st.session_state.project_type} Studio")
    st.caption(f"Mode: {st.session_state.work_style}")
    st.divider()

    # INPUT TABS
    tab1, tab2 = st.tabs(["🔴 Record", "📂 Upload"])
    audio_data = None
    with tab1:
        audio_rec = st.audio_input("Record Audio")
        if audio_rec: audio_data = audio_rec
    with tab2:
        audio_up = st.file_uploader("Upload File", type=['mp3','wav','m4a'])
        if audio_up: audio_data = audio_up

    # PROCESS
    if audio_data:
        if st.button("⚡ Run Rhythm Logic"):
            with st.spinner("Processing..."):
                result = run_rhythm_logic(audio_data, st.session_state.project_type, st.session_state.work_style, api_key, st.session_state.last_draft)
                st.session_state.last_draft = result
                st.rerun()

    # OUTPUT & EDIT
    if st.session_state.last_draft:
        st.success("Result Generated")
        
        # Text Editor
        new_text = st.text_area("Workspace", st.session_state.last_draft, height=400)
        st.session_state.last_draft = new_text
        
        # Download
        st.download_button("💾 Save to Device", st.session_state.last_draft, "RL_Draft.txt")
        
        # Refinement Chat
        st.divider()
        st.markdown("#### 🎬 Director's Chair")
        user_instruct = st.text_input("Give feedback to refine this draft...", placeholder="Ex: Make the tone darker...")
        if st.button("Update Draft"):
            if user_instruct:
                with st.spinner("Refining..."):
                    updated = text_chat(user_instruct, st.session_state.last_draft, api_key)
                    st.session_state.last_draft = updated
                    st.rerun()