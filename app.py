import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# --- 1. SETUP ---
st.set_page_config(page_title="Rhythm Logic GPS v26.0", page_icon="📱", layout="centered")

# --- 2. THE WORKING CONFIGURATION ---
# We are using the exact URL that worked in your Debug test.
# NO SLASH at the end.
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
        except Exception as e:
            st.error(f"Login Failed: {e}")
            return None
    return None

def get_login_url():
    flow = get_auth_flow()
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url

# --- 3. DRIVE UPLOAD ---
def upload_audio_draft(service, audio_bytes):
    # Quick connect to Drive
    file_metadata = {'name': 'Rhythm_Logic_Audio_Draft.wav'} 
    media = MediaIoBaseUpload(io.BytesIO(audio_bytes), mimetype='audio/wav')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

# --- 4. THE UI ---
st.title("Rhythm Logic GPS v26.0")
st.markdown("### 🚧 Integration Mode")

# A. RESET BUTTON (Crucial for fixing the loop)
if st.button("🔄 RESET / LOGOUT (Click this if stuck)"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.query_params.clear()
    st.rerun()

# B. AUTHENTICATION
if "creds" not in st.session_state:
    creds = authenticate_google()
    
    if not creds:
        url = get_login_url()
        st.info(f"Targeting Redirect URI: {REDIRECT_URI}")
        st.markdown(f'[👉 **CLICK HERE TO SIGN IN**]({url})')
        st.caption("If you get a 403 error, click 'Request Details' on the error page and check the redirect_uri.")
    else:
        st.session_state["creds"] = creds
        st.rerun()

# C. THE STUDIO (Only shows if logged in)
else:
    st.success("✅ YOU ARE IN.")
    st.write("The connection is stable.")
    
    service = build('drive', 'v3', credentials=st.session_state['creds'])
    
    audio_value = st.audio_input("Record Chapter")
    
    if audio_value:
        with st.spinner("Uploading to Drive root folder..."):
            file_id = upload_audio_draft(service, audio_value.getvalue())
            st.success(f"Uploaded! File ID: {file_id}")