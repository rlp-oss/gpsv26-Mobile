import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# --- 1. SETUP & GOLD BRANDING ---
st.set_page_config(
    page_title="Rhythm Logic GPS v26.0", 
    page_icon="📱", 
    layout="centered"
)

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton button { width: 100%; border-radius: 20px; font-weight: bold; background-color: #d4af37; color: black; border: none; }
    h1 { color: #d4af37; text-align: center; font-family: 'Helvetica', sans-serif; text-transform: uppercase; letter-spacing: 2px; }
    .caption { text-align: center; color: #888; font-size: 12px; letter-spacing: 1px; }
    .login-btn { background-color: #d4af37; color: black; padding: 15px 32px; text-align: center; display: block; font-size: 16px; border-radius: 12px; width: 100%; font-weight: bold; margin-top: 20px; text-decoration: none;}
    a { text-decoration: none; }
    /* Hide the deploy button to make it look like a real app */
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# --- 2. THE "REPAIR MODE" ENGINE (HIDDEN) ---
# We are using the exact hardcoded link that just worked for you.
# DO NOT CHANGE THIS LINE.
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

def authenticate():
    flow = get_auth_flow()
    if "code" in st.query_params:
        try:
            code = st.query_params["code"]
            flow.fetch_token(code=code)
            st.query_params.clear() # Clear the URL so we don't loop
            return flow.credentials
        except Exception:
            st.query_params.clear()
            return None
    return None

def get_login_url():
    flow = get_auth_flow()
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url

# --- 3. DRIVE LOGIC ---
def get_rhythm_logic_folder(service):
    """Finds or Creates the 'Rhythm Logic Studio' folder"""
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
        return None 

def upload_audio_draft(service, folder_id, audio_bytes):
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

# --- SAFETY NET (Hidden in Sidebar) ---
# If you ever get stuck, open sidebar and click Reset.
with st.sidebar:
    st.markdown("### ⚙️ System")
    if st.button("🔄 Reset / Sign Out"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.query_params.clear()
        st.rerun()

# --- MAIN APP ---
if "creds" not in st.session_state:
    creds = authenticate()
    if not creds:
        # LOGIN SCREEN
        st.info("🔒 Secure Cloud Workspace")
        st.write("Connect to Google Drive to sync your voice notes.")
        url = get_login_url()
        st.markdown(f'<a href="{url}" target="_self"><div class="login-btn">👉 SIGN IN WITH GOOGLE</div></a>', unsafe_allow_html=True)
    else:
        st.session_state["creds"] = creds
        st.rerun()

else:
    # STUDIO SCREEN
    service = build('drive', 'v3', credentials=st.session_state['creds'])
    
    # Silent Connect
    studio_folder_id = get_rhythm_logic_folder(service)
    
    st.subheader("🎙️ Dictation Studio")
    st.success("Ready to record.")
    
    audio_value = st.audio_input("Record Chapter")
    
    if audio_value:
        with st.spinner("Syncing to Cloud..."):
            upload_audio_draft(service, studio_folder_id, audio_value.getvalue())
            st.toast("Saved to 'Rhythm Logic Studio'! 💾")
            st.balloons()