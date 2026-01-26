import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

st.set_page_config(page_title="Rhythm Logic Diagnostic", page_icon="🔧")

# --- 1. HARDCODED SETTINGS (The Source of Truth) ---
# This is the link we are forcing the app to use.
# It has NO SLASH at the end.
REAL_REDIRECT_URI = "https://gpsv26-mobile-ze6vywftyjsfzpgf9ogrga.streamlit.app"

# --- 2. THE DIAGNOSTIC HEADER ---
st.title("🔧 Repair Mode")
st.write("We are going to match these settings 100% with Google.")

st.warning("👇 STEP 1: COPY THIS EXACT LINK:")
st.code(REAL_REDIRECT_URI, language="text")
st.write("Go to **Google Cloud Console > Credentials > OAuth Client**.")
st.write("Paste that link into 'Authorized redirect URIs'. **Delete any others.**")

st.divider()

# --- 3. AUTH LOGIC ---
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
    if "code" in st.query_params:
        try:
            code = st.query_params["code"]
            flow.fetch_token(code=code)
            return flow.credentials
        except Exception as e:
            st.error(f"Token Error: {e}")
            return None
    return None

# --- 4. EXECUTION ---
if "creds" not in st.session_state:
    creds = authenticate()
    if not creds:
        flow = get_auth_flow()
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        st.info("👇 STEP 2: CLICK TO TEST")
        st.markdown(f"[**👉 ATTEMPT LOGIN**]({auth_url})")
        
        st.write("---")
        st.caption("If you see a 403 Error, click 'Error Details' on that page.")
        st.caption(f"It must say: redirect_uri={REAL_REDIRECT_URI}")
    else:
        st.session_state["creds"] = creds
        st.rerun()

else:
    st.success("✅ SUCCESS! The connection is fixed.")
    st.write("Now we can add the recorder back.")
    
    # Simple Recorder Test
    service = build('drive', 'v3', credentials=st.session_state['creds'])
    audio_value = st.audio_input("Test Microphone")
    if audio_value:
        st.write("Uploading...")
        file_metadata = {'name': 'Diagnostic_Test_Audio.wav'}
        media = MediaIoBaseUpload(io.BytesIO(audio_value.getvalue()), mimetype='audio/wav')
        service.files().create(body=file_metadata, media_body=media).execute()
        st.toast("Upload Worked!")