import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Rhythm Logic GPS - Pocket Publisher",
    page_icon="🚀",
    layout="wide" # Wide layout for a "website" feel
)

# --- YOUR GUMROAD LINK ---
GUMROAD_LINK = "https://rhythmlogic.gumroad.com/l/dldqoy"

# --- CUSTOM CSS (The "ClickFunnels" Look) ---
st.markdown("""
<style>
    /* REMOVE STREAMLIT BRANDING */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* GLOBAL STYLES */
    .stApp { background-color: #000000; color: white; font-family: 'Helvetica Neue', sans-serif; }
    
    /* HERO SECTION */
    .hero-container { text-align: center; padding: 40px 20px; }
    .main-headline { 
        font-size: 60px; 
        font-weight: 800; 
        background: -webkit-linear-gradient(#d4af37, #fcf6ba); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        margin-bottom: 10px;
    }
    .sub-headline { font-size: 24px; color: #ccc; margin-bottom: 30px; }
    
    /* VIDEO PLACEHOLDER */
    .video-box { 
        border: 2px solid #333; 
        border-radius: 20px; 
        padding: 10px; 
        background-color: #111;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.2);
    }
    
    /* CTA BUTTON */
    .cta-button {
        background-color: #d4af37; 
        color: black; 
        padding: 20px 40px; 
        font-size: 24px; 
        font-weight: bold; 
        border-radius: 50px; 
        text-decoration: none; 
        display: inline-block;
        margin-top: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4);
        transition: transform 0.2s;
    }
    .cta-button:hover { transform: scale(1.05); background-color: #fff; color: black;}
    
    /* FEATURE BOXES */
    .feature-card {
        background-color: #1a1a1a;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #333;
        text-align: left;
        height: 100%;
    }
    .feature-icon { font-size: 40px; margin-bottom: 10px; }
    .feature-title { font-size: 20px; font-weight: bold; color: #d4af37; }
    
    /* THE STACK */
    .stack-container {
        border: 2px dashed #444;
        background-color: #0e0e0e;
        padding: 40px;
        border-radius: 20px;
        margin-top: 50px;
    }
    .stack-item { font-size: 18px; margin-bottom: 10px; border-bottom: 1px solid #222; padding-bottom: 10px;}
    .stack-value { float: right; color: #d4af37; font-weight: bold; }
    .total-price { font-size: 32px; font-weight: bold; color: white; text-align: center; margin-top: 20px;}
    .real-price { font-size: 48px; font-weight: 900; color: #d4af37; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- HERO SECTION ---
st.markdown(f"""
<div class='hero-container'>
    <div class='main-headline'>STOP LOSING YOUR BEST IDEAS.</div>
    <div class='sub-headline'>The AI "Pocket Publisher" that turns your messy voice notes into polished books, lyrics, and content—instantly.</div>
    
    <div class='video-box'>
        <img src="https://images.unsplash.com/photo-1555421689-d68471e189f2?q=80&w=2070&auto=format&fit=crop" style="width: 100%; border-radius: 10px; opacity: 0.6;">
        <p style="color: #888; margin-top: 10px;">(Your 60-Second Demo Video Goes Here)</p>
    </div>

    <a href="{GUMROAD_LINK}" target="_blank" class="cta-button">👉 GET INSTANT ACCESS</a>
    <p style="color: #666; font-size: 14px;">Instant Activation • Cancel Anytime</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- THE PROBLEM / AGITATION ---
col1, col2 = st.columns([1, 1])

with col1:
    st.image("https://images.unsplash.com/photo-1516387938699-a93567ec168e?q=80&w=2071&auto=format&fit=crop", caption="The Old Way")

with col2:
    st.markdown("""
    ### ❌ The Problem: Friction Kills Creativity.
    
    You're driving. You're walking the dog. You're lying in bed.
    
    **BAM.** A million-dollar idea hits you.
    
    But by the time you unlock your phone, open your notes app, and try to type it out with your thumbs... **the magic is gone.**
    
    Typing on glass is slow. It's tedious. And it's stopping you from finishing your book or song.
    """)

st.write("")
st.write("")

# --- THE SOLUTION ---
st.markdown("<h2 style='text-align: center; color: white;'>✅ The Solution: Rhythm Logic GPS</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ccc;'>It listens. It understands. It writes.</p>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class='feature-card'>
        <div class='feature-icon'>📖</div>
        <div class='feature-title'>Book Chapters</div>
        <p>Ramble about your plot for 2 minutes. Get back a structured, professionally written chapter draft.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class='feature-card'>
        <div class='feature-icon'>🎵</div>
        <div class='feature-title'>Songwriter Mode</div>
        <p>Sing "bop bop bee doo" and tell it the vibe. It writes the lyrics, rhyme scheme, and structure.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class='feature-card'>
        <div class='feature-icon'>🎬</div>
        <div class='feature-title'>The Director's Chair</div>
        <p>Don't like the draft? Just tell it: "Make it darker" or "Add a bridge," and it rewrites it instantly.</p>
    </div>
    """, unsafe_allow_html=True)

# --- THE OFFER STACK (The "No-Brainer") ---
st.markdown("""
<div class='stack-container'>
    <h2 style='text-align: center; color: white; text-transform: uppercase;'>📦 What You Get Today</h2>
    <br>
    <div class='stack-item'>📱 <b>Rhythm Logic Mobile Studio</b> <span class='stack-value'>($20/mo Value)</span></div>
    <div class='stack-item'>🤖 <b>The "Director's Chair" Engine</b> <span class='stack-value'>($15/mo Value)</span></div>
    <div class='stack-item'>⚡ <b>Unlimited "Spark" Ideas</b> <span class='stack-value'>($10/mo Value)</span></div>
    <div class='stack-item'>🔒 <b>Secure Cloud Storage</b> <span class='stack-value'>(Included)</span></div>
    <div class='stack-item'>🎁 <b>BONUS: "Dictate Your Book" PDF Guide</b> <span class='stack-value'>($27 Value)</span></div>
    
    <div class='total-price'>Total Value: <span style='text-decoration: line-through; color: #888;'>$72/month</span></div>
    <div class='real-price'>ONLY $20<span style='font-size: 20px; color: #aaa;'>/month</span></div>
    
    <div style='text-align: center;'>
        <a href="{GUMROAD_LINK}" target="_blank" class="cta-button">👉 START CREATING NOW</a>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")
st.divider()

# --- FAQ ---
st.markdown("### ❓ Frequently Asked Questions")

with st.expander("Does this work on iPhone and Android?"):
    st.write("Yes. It runs directly in your browser. No app store download required.")

with st.expander("Is my voice data private?"):
    st.write("Yes. We use your secure API key. Your ideas stay yours.")

with st.expander("Can I cancel anytime?"):
    st.write("Absolutely. Cancel via Gumroad in 1 click.")

st.markdown("<br><br><p style='text-align: center; color: #444;'>© 2026 Rhythm Logic Publishing</p>", unsafe_allow_html=True)