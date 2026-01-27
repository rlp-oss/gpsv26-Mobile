import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Cody Germain | Official Hub", page_icon="👑", layout="wide")

# --- CUSTOM CSS (The "Empire" Theme) ---
st.markdown("""
<style>
    /* GLOBAL THEME */
    .stApp { background-color: #050505; color: white; }
    h1, h2, h3 { font-family: 'Helvetica Neue', sans-serif; text-transform: uppercase; letter-spacing: 1px; }
    h1 { color: #d4af37; font-weight: 900; }
    h2 { color: white; border-bottom: 2px solid #333; padding-bottom: 10px; }
    a { text-decoration: none; }

    /* CARDS */
    .app-card {
        background-color: #1a1a1a;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 20px;
        height: 240px; 
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .app-card:hover {
        transform: translateY(-5px);
        border-color: #d4af37;
        box-shadow: 0 10px 20px rgba(212, 175, 55, 0.1);
    }
    .card-title { font-size: 18px; font-weight: bold; color: #fff; margin-bottom: 5px; }
    .card-desc { font-size: 13px; color: #aaa; margin-bottom: 15px; line-height: 1.4; }
    
    /* BADGES */
    .badge-ent { background-color: #444; color: #d4af37; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #d4af37; }
    .badge-app { background-color: #222; color: #ccc; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }

    /* BUTTONS */
    .action-btn {
        background-color: #d4af37;
        color: black;
        text-align: center;
        padding: 10px;
        border-radius: 6px;
        font-weight: bold;
        display: block;
        transition: background 0.2s;
    }
    .action-btn:hover { background-color: #fff; }
    
    /* HERO SECTION */
    .hero {
        text-align: center;
        padding: 40px 20px;
        background: radial-gradient(circle at center, #222 0%, #000 100%);
        border-radius: 20px;
        margin-bottom: 40px;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 📂 YOUR REAL DATABASE
# ==========================================

# 1. SOFTWARE (From your Gumroad Screenshot)
SOFTWARE = [
    {"name": "RL Global Academy", "desc": "The Global Education Tool Free For The World Web App (Mobile or Desktop) .", "tag": "ENTERPRISE", "url": "https://rhythmlogicglobalacademy.streamlit.app/"},
    {"name": "Rhythm Logic Software", "desc": "The Official Rhythm Logic Sales Page.", "tag": "ENTERPRISE", "url": "https://rhythmlogic.gumroad.com/?_gl=1*1ydx5o7*_ga*MTA1MTI1MTMxNi4xNzY5NDcyMDQ4*_ga_6LJN6D94N6*czE3Njk1NDc4NzMkbzUkZzEkdDE3Njk1NDc4NzgkajU1JGwwJGgw"},
    {"name": "Rhythm Logic Publishing", "desc": "Fast Professional Full Stack Publishing Services", "tag": "ENTERPRISE", "url": "https://rhythmlogicpublishing.com/"},
    {"name": "Rhythm Logic Mobile", "desc": "The Pocket Publisher. Write books on the go.", "tag": "ENTERPRISE", "url": "https://gpsv26-mobile.streamlit.app/"},
    # 
]

# 2. BOOKS (From your WildWarp/BubbleBum Screenshots)
BOOKS = [
    {"title": "The Bluetooth Paradox", "series": "WildWarp Chronicles", "img": "https://m.media-amazon.com/images/I/81xlyd9y2FL._SL1500_.jpg", "url": "https://a.co/d/cjmKEPo"},
    {"title": "The Quantum Corral", "series": "WildWarp Chronicles", "img": "https://m.media-amazon.com/images/I/81ywZpXuU5L._SL1500_.jpg", "url": "https://a.co/d/9Q5H9f0"},
    {"title": "The Master Clock", "series": "WildWarp Chronicles", "img": "https://m.media-amazon.com/images/I/81ZAGR4W3LL._SL1500_.jpg", "url": "https://a.co/d/2UShIjq"},
    {"title": "BubbleBum Universe", "series": "Kids Collection", "img": "https://ih0.redbubble.net/avatar.10585962.140x140.jpg", "url": "https://bubblebumbooks.com/"},
]

# 3. MERCH LINKS
MERCH_LINKS = {
    "Mila Moo": "https://www.redbubble.com/people/Bubblebum-Books/shop", 
    "WildWarp": "https://bubblebumbooks.com/wildwarp-chronicles",
    "Rhythm Logic": "https://rhythmlogic.gumroad.com/"  # <--- Pointing to Gumroad now
}

# ==========================================
# 🖥️ THE FRONT END
# ==========================================

# --- HEADER ---
col1, col2, col3 = st.columns([1,6,1])
with col2:
    st.markdown("<h1 style='text-align: center;'>CODY GERMAIN</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; letter-spacing: 4px; font-size: 12px;'>THE DIGITAL PORTFOLIO</p>", unsafe_allow_html=True)

st.divider()

# --- HERO: THE FLAGSHIP (The Cash Cow) ---
st.markdown("""
<div class='hero'>
    <h2 style='border:none; color: #d4af37;'>🚀 START HERE: RHYTHM LOGIC GPS</h2>
    <p style='color: #ccc; max-width: 600px; margin: 0 auto 20px auto;'>
        The AI-powered writing assistant that turns your voice into polished books, lyrics, and content.
    </p>
    <a href='https://rhythm-logic-live.streamlit.app/' target='_blank'>
        <button style='background-color: #d4af37; border: none; padding: 15px 40px; font-size: 18px; font-weight: bold; border-radius: 50px; cursor: pointer;'>
            LAUNCH MOBILE STUDIO
        </button>
    </a>
</div>
""", unsafe_allow_html=True)

# --- NAVIGATION TABS ---
tabs = st.tabs(["💻 SOFTWARE SUITE", "📚 THE BOOKSTORE", "👕 MERCH SHOP"])

# --- TAB 1: SOFTWARE (The 35 Titles) ---
with tabs[0]:
    c1, c2 = st.columns([3,1])
    with c1: st.markdown("### ⚡ Enterprise & Creative Tools")
    with c2: search = st.text_input("🔍 Search Tools...", placeholder="e.g. Enterprise")
    
    # Filter Logic
    filtered_apps = [app for app in SOFTWARE if search.lower() in app['name'].lower() or search.lower() in app['desc'].lower()]
    
    # Grid Layout
    cols = st.columns(3)
    for i, app in enumerate(filtered_apps):
        with cols[i % 3]:  # 
            tag_class = "badge-ent" if app['tag'] == "ENTERPRISE" else "badge-app"
            st.markdown(f"""
            <div class='app-card'>
                <div>
                    <div class='card-title'>{app['name']}</div>
                    <span class='{tag_class}'>{app['tag']}</span>
                    <div class='card-desc' style='margin-top: 10px;'>{app['desc']}</div>
                </div>
                <a href="{app['url']}" target="_blank" class="action-btn">GET ACCESS ↗</a>
            </div>
            """, unsafe_allow_html=True)

# --- TAB 2: BOOKS (WildWarp & BubbleBum) ---
with tabs[1]:
    st.markdown("### 📖 The Library")
    
    # Display Books in a 4-column grid
    b_cols = st.columns(4)
    for i, book in enumerate(BOOKS):
        with b_cols[i % 4]:
            st.image(book['img'], use_container_width=True)
            st.markdown(f"**{book['title']}**")
            st.caption(book['series'])
            st.markdown(f"[Order on Amazon]({book['url']})")

# --- TAB 3: MERCH ---
with tabs[2]:
    st.markdown("### 🧢 Character Merchandise")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.info("**🐶 Mila Moo Collection**\nGear for dog lovers.")
        st.link_button("Shop Redbubble", MERCH_LINKS["Mila Moo"])
    with m2:
        st.info("**💀 WildWarp Gear**\nSci-Fi apparel & accessories.")
        st.link_button("Shop Amazon", MERCH_LINKS["WildWarp"])
    with m3:
        st.info("**🚀 Rhythm Logic Swag**\nOfficial brand merchandise.")
        # This now correctly grabs the Gumroad link we defined above
        st.link_button("Shop Gumroad", MERCH_LINKS["Rhythm Logic"])