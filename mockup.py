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

st.title("🕯️ The Studio Mockup")
st.markdown("Upload your flat cover. We'll place it in a dramatic scene.")

# --- 1. GET THE BACKGROUND (REAL PHOTO) ---
# We use a specific high-quality Unsplash image of a dark table/library
# This ensures it always looks real, not like "computer noise"
BG_URL = "https://images.unsplash.com/photo-1541963463532-d68292c34b19?q=80&w=1920&auto=format&fit=crop"

def get_background():
    response = requests.get(BG_URL, stream=True)
    bg = Image.open(response.raw).convert("RGBA")
    # Darken and blur the background to keep focus on the book
    bg = bg.filter(ImageFilter.GaussianBlur(5)) 
    enhancer = ImageEnhance.Brightness(bg)
    bg = enhancer.enhance(0.4) # Make it moody/dark
    return bg

# --- 2. BUILD THE 3D BOOK OBJECT ---
def create_3d_book(cover_img):
    # Standardize size
    w, h = 600, 900
    cover = cover_img.resize((w, h), Image.Resampling.LANCZOS)
    
    # Create Spine
    spine_width = 60
    spine = cover.crop((0, 0, spine_width, h))
    spine = ImageOps.colorize(spine.convert("L"), black="#111", white="#444") # Dark spine
    spine = spine.resize((spine_width, h))
    
    # Create Book Block
    total_w = w + spine_width
    book = Image.new("RGBA", (total_w + 50, h + 20), (0,0,0,0))
    
    # Draw Page Block (The white paper edges)
    draw = ImageDraw.Draw(book)
    # Right side pages
    draw.rectangle([(spine_width + 10, 10), (total_w + 15, h - 10)], fill="#ddd")
    # Bottom pages curve
    draw.polygon([(spine_width + 10, h - 10), (total_w + 15, h - 10), (total_w + 5, h + 15), (spine_width + 20, h + 15)], fill="#ccc")

    # Paste Spine & Cover
    book.paste(spine, (0, 5))
    book.paste(cover, (spine_width, 0))
    
    return book

# --- 3. THE REFLECTION ENGINE ---
def add_reflection(book_img):
    # Flip the book vertically
    reflection = ImageOps.flip(book_img)
    # Blur it heavily
    reflection = reflection.filter(ImageFilter.GaussianBlur(15))
    
    # Create a gradient mask to fade it out
    mask = Image.new("L", book_img.size, 0)
    draw = ImageDraw.Draw(mask)
    # Draw gradient from opaque (top) to transparent (bottom)
    for y in range(book_img.height):
        alpha = int(255 * (1 - (y / (book_img.height * 0.4)))) # Fade out quickly
        if alpha < 0: alpha = 0
        draw.line([(0, y), (book_img.width, y)], fill=alpha)
    
    reflection.putalpha(mask)
    return reflection

# --- 4. COMPOSITOR ---
def composite_scene(user_cover):
    # Load Scene
    scene = get_background()
    scene_w, scene_h = scene.size
    
    # Create Book
    book = create_3d_book(user_cover)
    
    # Resize Book to fit scene (about 40% height)
    scale_factor = (scene_h * 0.55) / book.height
    new_w = int(book.width * scale_factor)
    new_h = int(book.height * scale_factor)
    book = book.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Position (Center X, Bottom Y)
    x_pos = (scene_w - new_w) // 2
    y_pos = (scene_h // 2) + 50 # Sits on the "table"
    
    # Create Reflection
    reflection = add_reflection(book)
    
    # Create Drop Shadow (Contact shadow)
    shadow = Image.new("RGBA", (new_w, 20), (0,0,0, 180))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    
    # Paste Order: Reflection -> Shadow -> Book
    # Paste Reflection (shifted down)
    scene.paste(reflection, (x_pos, y_pos + new_h - 10), mask=reflection)
    # Paste Shadow
    scene.paste(shadow, (x_pos, y_pos + new_h - 5), mask=shadow)
    # Paste Book
    scene.paste(book, (x_pos, y_pos), mask=book)
    
    # Add "Spotlight" Overlay (Warm light from top)
    # Create a radial gradient light
    overlay = Image.new("RGBA", scene.size, (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    
    # Warm center, Dark edges (Vignette)
    # We do this by drawing a massive black circle with a hole in it, essentially
    # But a simpler way in PIL is to create a darkness layer and mask out the center
    darkness = Image.new("RGBA", scene.size, (0,0,0, 150))
    
    # Create the "Light Mask"
    light_mask = Image.new("L", scene.size, 0)
    d_mask = ImageDraw.Draw(light_mask)
    # Draw a big fuzzy white circle in the middle
    center_x, center_y = scene_w // 2, scene_h // 2
    radius = 500
    d_mask.ellipse([(center_x - radius, center_y - radius - 200), (center_x + radius, center_y + radius)], fill=255)
    light_mask = light_mask.filter(ImageFilter.GaussianBlur(100))
    
    # Composite the darkness using the inverted mask
    scene = Image.composite(scene, Image.alpha_composite(scene, darkness), light_mask)

    return scene

# --- INTERFACE ---
uploaded_file = st.file_uploader("Upload Cover (JPG/PNG)", type=['jpg','png','jpeg'])

if uploaded_file:
    with st.spinner("Setting the lights..."):
        image = Image.open(uploaded_file)
        result = composite_scene(image)
        
        st.divider()
        st.image(result, caption="The Studio Render", use_container_width=True)
        
        # Download
        buf = io.BytesIO()
        result.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="⬇️ Download High-Res Mockup",
            data=byte_im,
            file_name="studio_mockup.png",
            mime="image/png"
        )
        
        st.success("✨ Render Complete!")
        st.markdown("### 💡 Now let the AI write the book.")
        st.markdown(f"[**👉 Get Rhythm Logic GPS**](https://rhythm-logic-live.streamlit.app/)")