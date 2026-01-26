import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import json
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
    .stButton button { width: 100%; border-radius: 20px; font-weight: bold; background-color: #d4af37; color: black; }
    h1 { color: #d4af37; text-align: center; font-family: Impact, sans-serif; }
    .caption { text-align: center; color: #888; font-size: 14px; }
    a { text-decoration: none; }
    .login-btn { background-color: #d4af37; color: black; padding: 15px 32px; text-align: center; display: block; font-size: 16px; border-radius: 12px; width: 100%; font-weight: bold; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 2. AUTHENTICATION LOGIC (The Working Version) ---

def authenticate_google():
    """Handles the secure login flow using your verified Secrets"""
    
    # We grab the exact Redirect URI you saved in Secrets to prevent mismatches
    redirect_uri = st.secrets["web"]["redirect_uris"][0]
    
    client_config = {
        "web": {
            "client_id": st.secrets["web"]["client_id"],
            "client_secret": st.secrets["web"]["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=['https://www.googleapis.com/auth/drive.file'],
        redirect_uri=redirect_uri
    )

    # Check for the 'code' that Google sends back after login
    if "code" in st.query_params:
        code = st.query_params["code"]
        flow.fetch_token(code=code)
        st.query_params.clear() # Clean the URL
        return flow.credentials
        
    return None

def get_login_url():
    """Generates the link to Google"""
    redirect_uri = st.secrets["web"]["redirect_uris"][0]
    
    client_config = {
        "web": {
            "client_id": st.secrets["web"]["client_id"],
            "client_secret": st.secrets["web"]["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=['https://www.googleapis.com/auth/drive.file'],
        redirect_uri=redirect_uri
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url

# --- 3. GOOGLE DRIVE LOGIC ---

def get_rhythm_logic_folder(service):
    """Finds or Creates the 'Rhythm Logic Studio' folder"""
    query = "name='Rhythm Logic Studio' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces='drive').execute()
    items = results.get('files', [])
    
    if not items:
        file_metadata = {
            'name': 'Rhythm Logic Studio',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    else:
        return items[0]['id']

def upload_audio_draft(service, folder_id, audio_bytes, chapter_name):
    """Uploads the voice note to Drive"""
    file_metadata = {
        'name': f"{chapter_name}_Audio_Draft.wav",
        'parents': [folder_id]
    }
    media = MediaIoBaseUpload(io.BytesIO(audio_bytes), mimetype='audio/wav')
    service.files().create(body=file_metadata, media_body=media).execute()

# --- 4. THE MAIN APP INTERFACE ---

st.title("Rhythm Logic GPS v26.0")
st.markdown('<p class="caption">MOBILE PUBLISHER | ENTERPRISE EDITION</p>', unsafe_allow_html=True)
st.divider()

# A. CHECK LOGIN STATUS
if "creds" not in st.session_state:
    # Try to authenticate using the URL code
    creds = authenticate_google()
    
    if not creds:
        # SHOW LOGIN SCREEN
        st.info("🔒 Secure Cloud Login Required")
        st.write("Connect your Google Drive to save your work automatically.")
        
        login_url = get_login_url()
        st.markdown(f'<a href="{login_url}" target="_self"><div class="login-btn">👉 SIGN IN WITH GOOGLE</div></a>', unsafe_allow_html=True)
    else:
        # SAVE CREDS AND REFRESH
        st.session_state["creds"] = creds
        st.rerun()

# B. SHOW THE STUDIO (If Logged In)
else:
    service = build('drive', 'v3', credentials=st.session_state['creds'])
    
    # 1. Connect to Drive Folder
    with st.spinner("Syncing with Google Drive..."):
        studio_folder_id = get_rhythm_logic_folder(service)
    
    st.success(f"✅ Connected to Drive")
    
    # 2. Dictation Studio
    st.subheader("🎙️ Dictation Studio")
    st.info("Tap the microphone below to record your chapter.")
    
    audio_value = st.audio_input("Record Chapter")
    
    if audio_value:
        st.write("Processing Audio...")
        # Upload to Drive
        upload_audio_draft(service, studio_folder_id, audio_value.getvalue(), "New_Chapter")
        st.toast("Saved to 'Rhythm Logic Studio' folder! 💾")
        st.balloons()