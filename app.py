import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import json
import io

# --- 1. SETUP ---
st.set_page_config(page_title="Rhythm Logic GPS v26.0 Debug", page_icon="📱", layout="centered")

# --- 2. AUTHENTICATION ---
def get_login_url():
    # Force the trailing slash issue to be solved
    # We grab the URL from the browser logic directly
    redirect_uri = "https://gpsv26-mobile-ze6vywftyjsfzpgf9ogrga.streamlit.app"
    
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
    return auth_url, redirect_uri

def authenticate_google():
    # Same hardcoded URI here to match
    redirect_uri = "https://gpsv26-mobile-ze6vywftyjsfzpgf9ogrga.streamlit.app"
    
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
    
    if "code" in st.query_params:
        code = st.query_params["code"]
        flow.fetch_token(code=code)
        st.query_params.clear()
        return flow.credentials
    return None

# --- 3. UI ---
st.title("🚧 Debug Mode")

if "creds" not in st.session_state:
    creds = authenticate_google()
    if not creds:
        url, redirect = get_login_url()
        
        st.error("⚠️ CRITICAL SETTINGS CHECK")
        st.write("Go to Google Cloud Console > Credentials > OAuth Client.")
        st.write("Ensure 'Authorized redirect URIs' is EXACTLY this (copy-paste it):")
        st.code(redirect, language="text")
        
        st.markdown(f'[👉 CLICK HERE TO SIGN IN]({url})')
    else:
        st.session_state["creds"] = creds
        st.rerun()

else:
    st.success("You are logged in! The fix worked.")
    st.write("Now you can put the original code back.")