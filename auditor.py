import streamlit as st
from duckduckgo_search import DDGS
import requests
import pandas as pd
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="RL Brand Hunter", page_icon="🕵️‍♂️", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    h1 { color: #d4af37; font-family: 'Helvetica', sans-serif; text-transform: uppercase; }
    .status-live { color: #00ff00; font-weight: bold; }
    .status-dead { color: #ff0000; font-weight: bold; }
    .stDataFrame { border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

st.title("🕵️‍♂️ The Brand Hunter")
st.markdown("Scan the web for your brand keywords and find broken links.")

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("Search Settings")
    query = st.text_input("Enter Brand/Product Name:", "Rhythm Logic GPS")
    num_results = st.slider("Max Results to Scan:", 5, 50, 10)
    
    st.info("ℹ️ **How it works:**\nThis tool queries DuckDuckGo for your brand, extracts the URLs, and 'pings' them to see if they are valid.")

# --- THE SCANNING ENGINE ---
def check_link_status(url):
    try:
        # We spoof the headers so websites think we are a real browser, not a bot
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            return "🟢 LIVE (200)"
        elif response.status_code == 404:
            return "🔴 BROKEN (404)"
        elif response.status_code == 403:
            return "🟠 BLOCKED (403)"
        else:
            return f"⚠️ STATUS {response.status_code}"
    except requests.exceptions.Timeout:
        return "⏱️ TIMEOUT"
    except requests.exceptions.ConnectionError:
        return "💀 DEAD LINK"
    except Exception as e:
        return "❓ ERROR"

if st.button("🚀 Start Scan"):
    if not query:
        st.warning("Please enter a keyword.")
        st.stop()
        
    results_container = []
    
    # 1. SEARCH PHASE
    with st.status("🔍 Scanning the web...", expanded=True) as status:
        st.write(f"Searching for '{query}'...")
        
        try:
            # Using DuckDuckGo Search (No API Key needed)
            with DDGS() as ddgs:
                search_results = list(ddgs.text(query, max_results=num_results))
            
            st.write(f"✅ Found {len(search_results)} links. Checking health...")
            
            # 2. CHECK PHASE
            progress_bar = st.progress(0)
            
            for i, result in enumerate(search_results):
                title = result['title']
                link = result['href']
                
                # Check the link
                status_msg = check_link_status(link)
                
                # Add to data list
                results_container.append({
                    "Title": title,
                    "URL": link,
                    "Status": status_msg
                })
                
                # Update Progress
                progress_bar.progress((i + 1) / len(search_results))
                time.sleep(0.5) # Be polite to servers
            
            status.update(label="✅ Scan Complete!", state="complete", expanded=False)
            
        except Exception as e:
            st.error(f"Search failed: {e}")
            st.stop()

    # 3. RESULTS PHASE
    st.divider()
    st.subheader(f"📊 Audit Report: {query}")
    
    if results_container:
        df = pd.DataFrame(results_container)
        
        # Display as an interactive table
        st.dataframe(
            df, 
            column_config={
                "URL": st.column_config.LinkColumn("Link"),
                "Status": st.column_config.TextColumn("Health")
            },
            use_container_width=True
        )
        
        # Download Button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Download Audit Report (CSV)",
            csv,
            "brand_audit.csv",
            "text/csv",
            key='download-csv'
        )
        
        # Quick Stats
        live_count = len(df[df['Status'].str.contains("LIVE")])
        dead_count = len(df) - live_count
        
        col1, col2 = st.columns(2)
        col1.metric("Live Links", live_count)
        col2.metric("Issues Found", dead_count, delta_color="inverse")