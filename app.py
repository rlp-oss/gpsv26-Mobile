import warnings
warnings.filterwarnings("ignore") # Silence non-critical warnings

import streamlit as st
import google.generativeai as genai
import io

# --- 1. SETUP & BRANDING (The Gold Suit) ---
st.set_page_config(
    page_title="Rhythm Logic GPS", 
    page_icon="🎙️", 
    layout="centered"
)

# Custom Gold Branding
st.markdown("""
<style>
    /* Main Background */
    .stApp { background-color: #0e1117; color: white; }
    
    /* Gold Buttons */
    .stButton button { 
        width: 100%; 
        border-radius: 12px; 
        font-weight: bold; 
        background-color: #d4af37; 
        color: black; 
        border: none;
        padding: 15px 0px;
    }
    .stButton button:hover {
        background-color: #f4cf57;
        color: black;
    }

    /* Headers */
    h1 { color: #d4af37; text-align: center; font-family: 'Helvetica', sans-serif; text-transform: uppercase; letter-spacing: 2px; }
    h3 { color: white; text-align: center; font-weight: 300; font-size: 18px; }
    
    /* Input Fields */
    .stTextInput input { border-radius: 10px; }
    .stSelectbox div[data-baseweb="select"] { border-radius: 10px; }
    .stTextArea textarea { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("Rhythm Logic GPS")
st.markdown("### The Professional's Ghostwriter")

# --- 2. SECURITY CHECK ---
api_key = None

try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except:
    pass

if not api_key:
    st.warning("🔒 Security Check")
    api_key = st.text_input("Enter Gemini API Key:", type="password", placeholder="Paste key here...")
    
    if not api_key:
        st.info("Need a key? Get it free: https://aistudio.google.com/app/apikey")
        st.stop()

# --- 3. SESSION STATE (The Memory) ---
# This keeps your work safe so you can "chat" with the AI without losing the lyrics.
if "history" not in st.session_state:
    st.session_state["history"] = ""
if "last_draft" not in st.session_state:
    st.session_state["last_draft"] = ""

# --- 4. THE AI ENGINE ---
def engineer_content(audio_file, mode, key, current_draft=""):
    """Sends audio to Gemini and returns professional text + Questions."""
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    # If this is a refinement (we already have text), we change the prompt
    if current_draft:
        prompt = f"""
        You are an expert Ghostwriter for Rhythm Logic.
        The user wants to refine their current draft based on new instructions.
        
        CURRENT DRAFT:
        {current_draft}
        
        USER INSTRUCTION (Audio):
        Listen to the audio instructions and update the draft accordingly.
        
        OUTPUT FORMAT:
        1. The Updated Draft.
        2. "Rhythm Logic Strategy": Ask 3 short, punchy questions about what the user wants to do next (e.g., "Add a bridge?", "Change the tone?", "Expand the second verse?").
        """
    else:
        # First time generation
        prompt = f"""
        You are an expert Ghostwriter for Rhythm Logic.
        1. Listen to the user's audio.
        2. Transcribe it perfectly.
        3. REWRITE it into this professional format: {mode}.
        
        CRITICAL STEP:
        At the bottom of your response, create a section called "🔮 RHYTHM LOGIC STRATEGY".
        In this section, ask the user 3 strategic questions to help them expand the piece.
        Example: "Do you want me to write a Bridge for this?", "Should we make the second verse darker?", "Do you want a counter-melody?"
        """

    try:
        response = model.generate_content([
            prompt,
            {"mime_type": "audio/mp3", "data": audio_file.read()}
        ])
        return response.text
    except Exception as e:
        return f"Error: {e}"

def text_refinement(instruction_text, current_draft, key):
    """Allows text-based chatting to update the draft."""
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    You are an expert Ghostwriter. Update the draft based on the user's text request.
    
    CURRENT DRAFT:
    {current_draft}
    
    USER REQUEST:
    {instruction_text}
    
    OUTPUT FORMAT:
    1. The Updated Draft.
    2. "🔮 RHYTHM LOGIC STRATEGY": 3 new questions for the next step.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# --- 5. THE INTERFACE ---
st.divider()

# Mode Selection
mode = st.selectbox(
    "📝 Select Blueprint",
    [
        "Song Lyrics (Verse/Chorus)", 
        "Sci-Fi Story Scene", 
        "Business Email", 
        "Medical Note (SOAP)",
        "Legal Brief",
        "Blog Post"
    ]
)

# Audio Inputs
st.write("") 
tab1, tab2 = st.tabs(["🎙️ RECORD", "📂 UPLOAD"])

audio_data = None

with tab1:
    audio_data_recorded = st.audio_input("Tap to Record")
    if audio_data_recorded:
        audio_data = audio_data_recorded

with tab2:
    uploaded_file = st.file_uploader("Upload Audio File", type=["wav", "mp3", "m4a", "webm"])
    if uploaded_file:
        audio_data = uploaded_file

# --- 6. ACTION & DISPLAY ---

if audio_data:
    st.divider()
    if st.button("⚡ ENGAGE RHYTHM LOGIC"):
        with st.spinner("🎧 Listening & Strategizing..."):
            # We pass the existing draft if we have one, to allow audio refinements
            result = engineer_content(audio_data, mode, api_key, st.session_state["last_draft"])
        
        if "Error" in result:
            st.error(result)
        else:
            st.session_state["last_draft"] = result # Save to memory
            st.rerun() # Refresh to show the result in the editor below

# DISPLAY RESULTS (If they exist in memory)
if st.session_state["last_draft"]:
    st.success("Draft & Strategy Generated")
    
    # 1. The Output Box (Editable)
    edited_text = st.text_area("Live Editor", st.session_state["last_draft"], height=400)
    st.session_state["last_draft"] = edited_text # Allow manual edits to stick

    st.download_button(
        label="💾 Download Draft",
        data=st.session_state["last_draft"],
        file_name="Rhythm_Logic_Draft.txt",
        mime="text/plain"
    )

    st.divider()
    
    # 2. The Director's Chair (Refinement)
    st.markdown("### 🎬 Director's Chair")
    st.caption("Answer the AI's questions above, or give new instructions (e.g., 'Write a bridge based on Question 1')")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        refinement_instruction = st.text_input("Tell Rhythm Logic what to do next...", label_visibility="collapsed", placeholder="Ex: Add a chorus about heartbreak...")
    with col2:
        if st.button("🔄 Update"):
            if refinement_instruction:
                with st.spinner("Rewriting..."):
                    new_version = text_refinement(refinement_instruction, st.session_state["last_draft"], api_key)
                    st.session_state["last_draft"] = new_version
                    st.rerun()