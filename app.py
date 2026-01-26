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
</style>
""", unsafe_allow_html=True)

st.title("Rhythm Logic GPS")
st.markdown("### The Professional's Ghostwriter")

# --- 2. SECURITY CHECK (Simple & Unbreakable) ---
api_key = None

# Check Secrets First
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except:
    pass

# If no secret, ask manually (Prevents crashing)
if not api_key:
    st.warning("🔒 Security Check")
    api_key = st.text_input("Enter Gemini API Key:", type="password", placeholder="Paste key here...")
    
    if not api_key:
        st.info("Need a key? Get it free: https://aistudio.google.com/app/apikey")
        st.stop()

# --- 3. THE AI ENGINE ---
def engineer_content(audio_file, mode, key):
    """Sends audio to Gemini and returns professional text."""
    genai.configure(api_key=key)
    
    # Using Flash for speed and reliability
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    You are an expert Ghostwriter for Rhythm Logic.
    1. Listen to the user's audio.
    2. Transcribe it perfectly.
    3. REWRITE it into this professional format: {mode}.
    4. Ensure the tone is polished and ready for publication.
    """

    try:
        response = model.generate_content([
            prompt,
            {"mime_type": "audio/mp3", "data": audio_file.read()}
        ])
        return response.text
    except Exception as e:
        return f"Error: {e}"

# --- 4. THE INTERFACE ---
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
        "Blog Post",
        "Book Chapter"
    ]
)

# Audio Inputs (Clean Tabs)
st.write("") # Spacing
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

# --- 5. ACTION & SAVE ---
if audio_data:
    st.divider()
    if st.button("⚡ ENGAGE RHYTHM LOGIC"):
        with st.spinner("🎧 Listening & Engineering..."):
            result = engineer_content(audio_data, mode, api_key)
        
        if "Error" in result:
            st.error("Connection Error. Please check your API Key.")
            st.error(result)
        else:
            st.success("Draft Complete")
            
            # Display Result
            st.text_area("Final Output", result, height=350)
            
            # DOWNLOAD BUTTON (Safe Alternative to Drive)
            st.download_button(
                label="💾 Download Text File",
                data=result,
                file_name=f"Rhythm_Logic_{mode.split()[0]}.txt",
                mime="text/plain"
            )