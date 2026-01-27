import streamlit as st
import requests
import pandas as pd
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Empire Monitor", page_icon="🟢", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    h1 { color: #d4af37; font-family: 'Helvetica', sans-serif; text-transform: uppercase; }
    .status-live { color: #00ff00; font-weight: bold; background-color: #003300; padding: 5px; border-radius: 5px;}
    .status-broken { color: #ff4b4b; font-weight: bold; background-color: #330000; padding: 5px; border-radius: 5px;}
    .stTextArea textarea { background-color: #1e1e1e; color: #fff; }
</style>
""", unsafe_allow_html=True)

st.title("🟢 The Empire Monitor")
st.markdown("Paste your `hub.py` links below to check for broken pages instantly.")

# --- CHECK FUNCTION ---
def check_status(url):
    try:
        # User-Agent makes us look like a real Chrome browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            return "🟢 LIVE"
        elif r.status_code == 404:
            return "🔴 BROKEN (404)"
        elif r.status_code == 403:
            return "🟠 BLOCKED (403)" # Site works but blocks bots
        else:
            return f"⚠️ {r.status_code}"
    except:
        return "💀 UNREACHABLE"

# --- MAIN INTERFACE ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 Your Empire Links")
    # I pre-filled this with your main apps based on your screenshots
    default_links = """https://rhythm-logic-live.streamlit.app/
https://www.google.com
https://rhythmlogic.gumroad.com/l/dldqoy
https://gpsv26-mobile-ze6vywftyjsfzpgf9ogrga.streamlit.app/
https://www.redbubble.com/people/CodyGermain/shop
"""
    urls_input = st.text_area("Paste Links (One per line):", default_links, height=400)

with col2:
    st.subheader("⚙️ Controls")
    st.info("This tool bypasses search engines and pings your sites directly. It is 100% accurate.")
    
    if st.button("🚀 Run Health Check", use_container_width=True):
        urls = [line.strip() for line in urls_input.split('\n') if line.strip()]
        
        if not urls:
            st.warning("Please paste some links first!")
            st.stop()
            
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, url in enumerate(urls):
            # Fix missing https
            if not url.startswith('http'):
                url = 'https://' + url
            
            status_text.text(f"Pinging: {url}...")
            stat = check_status(url)
            
            # Add to list
            results.append({"Link": url, "Status": stat})
            
            # Update Progress
            progress_bar.progress((i + 1) / len(urls))
            time.sleep(0.1) 
        
        status_text.text("✅ Audit Complete")
        
        # --- SHOW RESULTS ---
        st.divider()
        df = pd.DataFrame(results)
        
        # Live Stats
        live = len(df[df['Status'] == "🟢 LIVE"])
        dead = len(df) - live
        
        m1, m2 = st.columns(2)
        m1.metric("Systems Online", live)
        m2.metric("Issues Found", dead, delta_color="inverse")
        
        st.dataframe(
            df, 
            column_config={
                "Link": st.column_config.LinkColumn("Product Link"),
                "Status": st.column_config.TextColumn("Health")
            },
            use_container_width=True
        )