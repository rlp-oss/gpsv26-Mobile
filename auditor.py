import streamlit as st
from duckduckgo_search import DDGS
import requests
import pandas as pd
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Empire Health Check", page_icon="🏥", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    h1 { color: #d4af37; font-family: 'Helvetica', sans-serif; text-transform: uppercase; }
    .status-live { color: #00ff00; font-weight: bold; }
    .status-broken { color: #ff4b4b; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🏥 The Empire Health Check")

# --- HELPER FUNCTION: CHECK LINK ---
def check_status(url):
    try:
        # User-Agent makes us look like a real Chrome browser, not a bot
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            return "🟢 LIVE"
        elif r.status_code == 404:
            return "🔴 BROKEN (404)"
        elif r.status_code == 403:
            return "🟠 BLOCKED (403)"
        else:
            return f"⚠️ {r.status_code}"
    except:
        return "💀 DEAD / TIMEOUT"

# --- TABS ---
tab1, tab2 = st.tabs(["🔍 Auto-Search", "📋 Manual Audit"])

# --- TAB 1: SEARCH THE WEB ---
with tab1:
    st.markdown("### Scan the web for your brand")
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Enter Brand Name:", "Rhythm Logic GPS")
    with col2:
        num = st.slider("Results:", 5, 20, 10)

    if st.button("🚀 Run Scan"):
        results_data = []
        status_bar = st.status("Scanning...", expanded=True)
        
        try:
            # FIX: We use 'backend="html"' which is less strict for Cloud Servers
            with DDGS() as ddgs:
                # We try getting results one by one
                raw_results = ddgs.text(query, max_results=num, backend="html")
                
                # Convert generator to list to check if empty
                results_list = list(raw_results)

            if not results_list:
                status.update(label="❌ No results found. (Cloud IP blocked)", state="error")
                st.error("DuckDuckGo blocked the search. Try the 'Manual Audit' tab!")
                st.stop()

            # Process Results
            progress = st.progress(0)
            for i, res in enumerate(results_list):
                title = res['title']
                link = res['href']
                status = check_status(link)
                
                results_data.append({"Title": title, "URL": link, "Status": status})
                progress.progress((i + 1) / len(results_list))
                time.sleep(0.2) # Polite delay
            
            status_bar.update(label="✅ Scan Complete", state="complete", expanded=False)
            
            # Show Table
            df = pd.DataFrame(results_data)
            st.dataframe(
                df, 
                column_config={"URL": st.column_config.LinkColumn("Link")},
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Search Engine Error: {e}")

# --- TAB 2: MANUAL AUDIT (THE RELIABLE WAY) ---
with tab2:
    st.markdown("### Check Your Empire Links")
    st.write("Paste your list of 35 apps/books/merch links here to check them all at once.")
    
    # Default list so it's not empty
    default_text = """https://rhythm-logic-live.streamlit.app/
https://www.google.com
https://this-website-does-not-exist-123.com"""
    
    urls_input = st.text_area("Paste Links (One per line):", default_text, height=200)
    
    if st.button("🏥 Check Health"):
        urls = [line.strip() for line in urls_input.split('\n') if line.strip()]
        
        manual_data = []
        prog_bar = st.progress(0)
        
        for i, url in enumerate(urls):
            # Ensure it has http
            if not url.startswith('http'):
                url = 'https://' + url
            
            stat = check_status(url)
            manual_data.append({"URL": url, "Status": stat})
            prog_bar.progress((i + 1) / len(urls))
        
        st.success("Check Complete!")
        df_manual = pd.DataFrame(manual_data)
        
        st.dataframe(
            df_manual, 
            column_config={"URL": st.column_config.LinkColumn("Link")},
            use_container_width=True
        )