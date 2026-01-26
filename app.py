import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# --- 1. SETUP & BRANDING ---
st.set_page_config(
    page_title="Rhythm Logic GPS v26.0", 
    page_icon="📱", 
    layout="centered"
)

# Custom Gold Branding
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton button { width: 100%; border-radius: 20px; font-weight: bold; background-color: #d4af37; color: black; border: none; }
    .stAudio { width: 100%; }
    h1 { color: #d4af37; text-align: center; font-family: 'Helvetica', sans-serif; text-transform: uppercase; letter-spacing: 2px; }
    .caption { text-align: center; color: #888; font-size: 12px; letter-spacing: 1px; }
    .login-btn { background-color: #d4af37; color: black; padding: 15px 32px; text-align: center; display: block; font-size: 16px; border-radius: 12px; width: 100%; font-weight: bold; margin-top: 20px; text-decoration: none;}
    a { text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# --- 2. THE AUTH ENGINE (Verified Working) ---
# We keep the hardcoded NO-SLASH URL because we know it works.
REDIRECT_URI = "https://gpsv26-mobile-ze6vywftyjsfzpgf9ogrga.streamlit.app"

def get_auth_flow():
    """Creates the connection using the verified settings"""
    client_config = {
        "web": {
            "client_id": st.secrets["web"]["client_id"],
            "client_secret": st.secrets["web"]["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI],
        }
    }
    return Flow.from_client_config(
        client_config,
        scopes=['https://www.googleapis.com/auth/drive.file'],
        redirect_uri=REDIRECT_URI
    )

def authenticate_google():
    flow = get_auth_flow()
    
    if "code" in st.query_params:
        code = st.query_params["code"]
        try:
            flow.fetch_token(code=code)
            st.query_params.clear()
            return flow.credentials
        except Exception:
            st.query_params.clear()
            return None
    return None

def get_login_url():
    flow = get_auth_flow()
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url

# --- 3. DRIVE FUNCTIONS ---
def get_rhythm_logic_folder(service):
    """Finds or Creates the 'Rhythm Logic Studio' folder to keep things organized"""
    try:
        query = "name='Rhythm Logic Studio' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=query, spaces='drive').execute()
        items = results.get('files', [])
        
        if not items:
            file_metadata = {'name': 'Rhythm Logic Studio', 'mimeType': 'application/vnd.google-apps.folder'}
            folder = service.files().create(body=file_metadata, fields='id').execute()
            return folder.get('id')
        else:
            return items[0]['id']
    except:
        return None # Fallback to root if search fails

def upload_audio_draft(service, folder_id, audio_bytes):
    # Naming the file with a timestamp could be a future upgrade, for now we use a standard name
    file_metadata = {'name': 'New_Chapter_Draft.wav'}
    if folder_id:
        file_metadata['parents'] = [folder_id]
        
    media = MediaIoBaseUpload(io.BytesIO(audio_bytes), mimetype='audio/wav')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

# --- 4. THE INTERFACE ---

st.title("RHYTHM LOGIC GPS")
st.markdown('<p class="caption">MOBILE PUBLISHER | ENTERPRISE EDITION</p>', unsafe_allow_html=True)
st.divider()

# A. AUTHENTICATION CHECK
if "creds" not in st.session_state:
    creds = authenticate_google()
    
    if not creds:
        # Show Clean Login Screen
        st.info("🔒 Secure Cloud Workspace")
        st.write("Connect to Google Drive to sync your voice notes.")
        
        url = get_login_url()
        st.markdown(f'<a href="{url}" target="_self"><div class="login-btn">👉 SIGN IN WITH GOOGLE</div></a>', unsafe_allow_html=True)
    else:
        st.session_state["creds"] = creds
        st.rerun()

# B. THE STUDIO (LOGGED IN)
else:
    # Sidebar for Logout
    with st.sidebar:
        st.write(f"**Connected** ✅")
        if st.button("Sign Out"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

    # Main Studio
    service = build('drive', 'v3', credentials=st.session_state['creds'])
    
    # Silent Connect
    studio_folder_id = get_rhythm_logic_folder(service)
    
    st.subheader("🎙️ Dictation Studio")
    st.success("Ready to record.")
    
    audio_value = st.audio_input("Record Chapter")
    
    if audio_value:
        with st.spinner("Syncing to Cloud..."):
            upload_audio_draft(service, studio_folder_id, audio_value.getvalue())
            st.toast("Saved to 'Rhythm Logic Studio' folder! 💾")
            st.balloons()