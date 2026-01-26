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
    a { color: #d4af37 !important; text-decoration: none; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. GOOGLE AUTHENTICATION LOGIC ---

def authenticate_google():
    """Real Google Login Flow"""
    
    # 1. Load the secrets we saved in Streamlit
    client_config = {
        "web": {
            "client_id": st.secrets["web"]["client_id"],
            "client_secret": st.secrets["web"]["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [st.secrets["web"]["redirect_uris"][0]],
        }
    }

    # 2. Set up the connection flow
    flow = Flow.from_client_config(
        client_config,
        scopes=['https://www.googleapis.com/auth/drive.file'],
        redirect_uri=st.secrets["web"]["redirect_uris"][0]
    )

    # 3. Check if we have an auth code from Google (after redirect)
    # Using the new st.query_params (Streamlit v1.30+)
    if "code" in st.query_params:
        code = st.query_params["code"]
        flow.fetch_token(code=code)
        credentials = flow.credentials
        st.session_state["creds"] = credentials
        # Clear the code from the URL so we don't loop
        st.query_params.clear()
        return credentials

    # 4. If we are NOT logged in, return None
    return None

def get_login_url():
    """Generates the link the user clicks to sign in"""
    client_config = {
        "web": {
            "client_id": st.secrets["web"]["client_id"],
            "client_secret": st.secrets["web"]["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [st.secrets["web"]["redirect_uris"][0]],
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=['https://www.googleapis.com/auth/drive.file'],
        redirect_uri=st.secrets["web"]["redirect_uris"][0]
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url

# --- 3. DRIVE FUNCTIONS ---

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
    file_metadata = {
        'name': f"{chapter_name}_Audio_Draft.wav",
        'parents': [folder_id]
    }
    media = MediaIoBaseUpload(io.BytesIO(audio_bytes), mimetype='audio/wav')
    service.files().create(body=file_metadata, media_body=media).execute()

# --- 4. THE APP INTERFACE ---

st.title("Rhythm Logic GPS v26.0")
st.markdown('<p class="caption">MOBILE PUBLISHER | ENTERPRISE EDITION</p>', unsafe_allow_html=True)
st.divider()

# CHECK LOGIN STATUS
if "creds" not in st.session_state:
    # Try to grab the token from the URL if they just returned from Google
    creds = authenticate_google()
    
    if not creds:
        # Show Login Button
        st.info("🔒 Secure Cloud Login Required")
        login_url = get_login_url()
        # We use a markdown link because it's smoother than a button redirect
        st.markdown(f'<a href="{login_url}" target="_self"><button style="background-color:#d4af37; border:none; color:black; padding:15px 32px; text-align:center; text-decoration:none; display:inline-block; font-size:16px; margin:4px 2px; cursor:pointer; border-radius:12px; width:100%;">👉 SIGN IN WITH GOOGLE</button></a>', unsafe_allow_html=True)
    else:
        st.rerun() # Refresh to show the studio
else:
    # --- LOGGED IN: SHOW STUDIO ---
    service = build('drive', 'v3', credentials=st.session_state['creds'])
    
    # 1. Initialize Folder
    with st.spinner("Connecting to your Google Drive..."):
        studio_folder_id = get_rhythm_logic_folder(service)
    
    st.success(f"✅ Connected to Drive")
    
    # 2. Studio UI
    st.subheader("🎙️ Dictation Studio")
    audio_value = st.audio_input("Record your Chapter")
    
    if audio_value:
        st.write("Processing Audio...")
        upload_audio_draft(service, studio_folder_id, audio_value.getvalue(), "Chapter_1")
        st.toast("Saved to 'Rhythm Logic Studio' in your Drive! 💾")