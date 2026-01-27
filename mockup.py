import streamlit as st
from PIL import Image, ImageOps, ImageDraw, ImageFilter, ImageEnhance
import io
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="Dramatic Book Generator", page_icon="🕯️", layout="centered")
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #d4af37; }
    h1 { font-family: 'Helvetica', sans-serif; letter-spacing: 2px; text-transform: uppercase; }
    .stButton button { width: 100%; border-radius: 5px; font-weight: bold; background-color: #d4af37; color: black; border: none; padding: 15px 0px; }
    .stButton button:hover { background-color: #f4cf57; color: black; }
</style>
""", unsafe_allow_html=True)

st.title("🕯️ The Library Studio")
st.markdown("Upload your cover. Get a professional library mockup.")

# --- 1. GET THE BACKGROUND (REAL LIBRARY) ---
# A true "Dark Academia" library background (Bookshelves, warm light, wood)
# This URL is specific to a dark library interior
BG_URL = "https://images.unsplash.com/photo-1481627838653-40d7a4861bc7?q=80&w=1920&auto=format&fit=crop"

def get_background():
    try:
        response = requests.get(BG_URL, stream=True, timeout=5)
        bg = Image.open(response.raw).convert("RGBA")
        # Blur it slightly to simulate "Portrait Mode" depth of field
        bg = bg.filter(ImageFilter.GaussianBlur(3)) 
        # Darken it slightly so the user's book pops
        enhancer = ImageEnhance.Brightness(bg)
        bg = enhancer.enhance(0.6) 
        return bg
    except:
        # Fallback if internet fails: Black background
        return Image.new("RGBA", (1920, 1080), (20, 10, 5, 255))

# --- 2. BUILD THE 3D BOOK OBJECT ---
def create_3d_book(cover_img):
    # Standardize size
    w, h = 600, 900
    cover = cover_img.resize((w, h), Image.Resampling.LANCZOS)
    
    # Create Spine
    spine_width = 50
    spine = cover.crop((0, 0, spine_width, h))
    spine = ImageOps.colorize(spine.convert("L"), black="#1a1a1a", white="#333") 
    spine = spine.resize((spine_width, h))
    
    # Create Book Block
    total_w = w + spine_width
    book = Image.new("RGBA", (total_w + 30, h + 20), (0,0,0,0))
    
    # Draw Page Block (The white paper edges)
    draw = ImageDraw.Draw(book)
    draw.rectangle([(spine_width + 5, 5), (total_w + 10, h - 5)], fill="#eee") # Pages
    
    # Paste Spine & Cover
    book.paste(spine, (0, 10))
    book.paste(cover, (spine_width, 0))
    
    return book

# --- 3. THE REFLECTION ENGINE ---
def add_reflection(book_img):
    reflection = ImageOps.flip(book_img)
    reflection = reflection.filter(ImageFilter.GaussianBlur(8))
    
    # Create fade mask
    mask = Image.new("L", book_img.size, 0)
    draw = ImageDraw.Draw(mask)
    # Stronger fade for a polished wood look
    for y in range(book_img.height):
        alpha = int(200 * (1 - (y / (book_img.height * 0.3)))) 
        if alpha < 0: alpha = 0
        draw.line([(0, y), (book_img.width, y)], fill=alpha)
    
    reflection.putalpha(mask)
    return reflection

# --- 4. COMPOSITOR ---
def composite_scene(user_cover):
    scene = get_background()
    scene_w, scene_h = scene.size
    
    book = create_3d_book(user_cover)
    
    # SCALING FIX: Make it 45% of screen height (Prevents cutting off)
    target_h = int(scene_h * 0.45) 
    scale_factor = target_h / book.height
    new_w = int(book.width * scale_factor)
    new_h = int(book.height * scale_factor)
    book = book.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # CENTERING FIX:
    # X: Perfect center
    # Y: Sitting in the bottom 3rd (on the table)
    x_pos = (scene_w - new_w) // 2
    y_pos = int(scene_h * 0.45) # Moves it up/down. 0.45 puts the base near the bottom third.
    
    # Create Reflection & Shadow
    reflection = add_reflection(book)
    shadow = Image.new("RGBA", (new_w, 20), (0,0,0, 160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(15))
    
    # COMPOSITE LAYERS
    # 1. Reflection (Below the book)
    scene.paste(reflection, (x_pos, y_pos + new_h - 5), mask=reflection)
    # 2. Shadow (Under the base)
    scene.paste(shadow, (x_pos, y_pos + new_h - 10), mask=shadow)
    # 3. The Book
    scene.paste(book, (x_pos, y_pos), mask=book)
    
    # 4. LIGHTING OVERLAY (Vignette)
    # Darken edges to focus on book
    vignette = Image.new("RGBA", scene.size, (0,0,0,0))
    # We cheat a vignette by drawing a massive radial gradient
    # Or simpler: Just a dark overlay with a hole cut out
    dark_layer = Image.new("RGBA", scene.size, (0,0,0, 100))
    mask = Image.new("L", scene.size, 0)
    draw = ImageDraw.Draw(mask)
    # Draw hole
    center_x, center_y = x_pos + new_w//2, y_pos + new_h//2
    draw.ellipse([(center_x - 600, center_y - 600), (center_x + 600, center_y + 600)], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(150))
    
    scene = Image.composite(scene, Image.alpha_composite(scene, dark_layer), mask)

    return scene

# --- INTERFACE ---
uploaded_file = st.file_uploader("Upload Cover (JPG/PNG)", type=['jpg','png','jpeg'])

if uploaded_file:
    with st.spinner("Entering the library..."):
        image = Image.open(uploaded_file)
        result = composite_scene(image)
        
        st.divider()
        st.image(result, caption="The Library Render", use_container_width=True)
        
        buf = io.BytesIO()
        result.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="⬇️ Download High-Res Mockup",
            data=byte_im,
            file_name="library_mockup.png",
            mime="image/png"
        )
        
        st.success("✨ Render Complete!")
        st.markdown("### 💡 This book deserves to be written.")
        st.markdown(f"[**👉 Get Rhythm Logic GPS**](https://rhythm-logic-live.streamlit.app/)")