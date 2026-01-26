import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# --- 1. SETUP ---
st.set_page_config(page_title="Rhythm Logic GPS", page_icon="📱", layout="centered")

# --- 2. THE DIAGNOSTIC ENGINE (EXACT COPY - DO NOT TOUCH) ---
# This is the exact link that worked in the test.
REAL_REDIRECT_URI = "https://gpsv26-mobile-ze6vywftyjsfzpgf9ogrga.streamlit.app"

def get_auth_flow():
    client_config = {
        "web": {
            "client_id": st.secrets["web"]["client_id"],
            "client_secret": st.secrets["web"]["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REAL_REDIRECT_URI],
        }
    }
    return Flow.from_client_config(
        client_config,
        scopes=['https://www.googleapis.com/auth/drive.file'],
        redirect_uri=REAL_REDIRECT_URI
    )

def authenticate():
    flow = get_auth_flow()
    # Only try to trade the code for a token if a code actually exists
    if "code" in st.query_params:
        try:
            code = st.query_params["code"]
            flow.fetch_token(code=code)
            st.query_params.clear() # IMMEDIATE CLEAR
            return flow.credentials
        except Exception:
            st.query_params.clear() # IMMEDIATE CLEAR ON FAIL
            return None
    return None

# --- 3. UI STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton button { width: 100%; border-radius: 20px; font-weight: bold; background-color: #d4af37; color: black; border: none; }
    h1 { color: #d4af37; text-align: center; font-family: 'Helvetica', sans-serif; text-transform: uppercase; letter-spacing: 2px; }
    .caption { text-align: center; color: #888; font-size: 12px; letter-spacing: 1px; }
    .login-btn { background-color: #d4af37; color: black; padding: 15px 32px; text-align: center; display: block; font-size: 16px; border-radius: 12px; width: 100%; font-weight: bold; margin-top: 20px; text-decoration: none;}
    a { text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# --- 4. EXECUTION LOGIC ---

st.title("RHYTHM LOGIC GPS")
st.markdown('<p class="caption">MOBILE PUBLISHER | ENTERPRISE EDITION</p>', unsafe_allow_html=True)
st.divider()

# SIDEBAR RESET (Your Escape Hatch)
with st.sidebar:
    if st.button("🔄 FORCE RESET"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.query_params.clear()
        st.rerun()

# AUTH CHECK
if "creds" not in st.session_state:
    creds = authenticate()
    if not creds:
        # Show Login Screen
        flow = get_auth_flow()
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        st.info("🔒 Secure Cloud Workspace")
        st.write("Connect to Google Drive to sync your voice notes.")
        st.markdown(f'<a href="{auth_url}" target="_self"><div class="login-btn">👉 SIGN IN WITH GOOGLE</div></a>', unsafe_allow_html=True)
    else:
        st.session_state["creds"] = creds
        st.rerun()

else:
    # STUDIO SCREEN (Only shows if logged in)
    service = build('drive', 'v3', credentials=st.session_state['creds'])
    
    # 1. Silent Folder Connect
    try:
        query = "name='Rhythm Logic Studio' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=query, spaces='drive').execute()
        items = results.get('files', [])
        if not items:
            file_metadata = {'name': 'Rhythm Logic Studio', 'mimeType': 'application/vnd.google-apps.folder'}
            folder = service.files().create(body=file_metadata, fields='id').execute()
            folder_id = folder.get('id')
        else:
            folder_id = items[0]['id']
    except:
        folder_id = None

    # 2. Recorder
    st.subheader("🎙️ Dictation Studio")
    st.success("Ready to record.")
    
    audio_value = st.audio_input("Record Chapter")
    
    if audio_value:
        with st.spinner("Syncing to Cloud..."):
            file_metadata = {'name': 'New_Chapter_Draft.wav'}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            media = MediaIoBaseUpload(io.BytesIO(audio_value.getvalue()), mimetype='audio/wav')
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            st.toast("Saved to 'Rhythm Logic Studio'! 💾")