import streamlit as st
from PIL import Image, ImageOps, ImageDraw, ImageFilter, ImageChops
import io
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="Dramatic Book Generator", page_icon="🕯️", layout="centered")

# --- CSS FOR THE VIBE ---
st.markdown("""
<style>
    .stApp { background-color: #0e0e0e; color: #d4af37; }
    h1 { color: #d4af37; text-transform: uppercase; }
    .stButton button { background-color: #d4af37; color: black; font-weight: bold; border: none;}
    .stButton button:hover { background-color: #f4cf57; }
</style>
""", unsafe_allow_html=True)

st.title("🕯️ The Dramatic Library Mockup")
st.markdown("Upload your flat cover to place it on a library desk under dramatic lighting.")

# --- HELPER FUNCTIONS ---
def create_radial_gradient(size, inner_color, outer_color):
    """Creates a radial gradient for the spotlight effect."""
    width, height = size
    # Create a radial gradient mask
    gradient = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(gradient)
    # Draw concentric circles to simulate radial gradient
    center_x, center_y = width // 2, height // 2
    max_radius = max(center_x, center_y) * 1.2
    for i in range(int(max_radius), 0, -1):
        color = int(255 * (1 - i / max_radius))
        draw.ellipse((center_x - i, center_y - i, center_x + i, center_y + i), fill=color, outline=color)
    gradient = gradient.filter(ImageFilter.GaussianBlur(radius=width//10))
    
    # Create color layers
    inner = Image.new('RGBA', size, inner_color)
    outer = Image.new('RGBA', size, outer_color)
    # Composite them using the gradient as mask
    return Image.composite(inner, outer, gradient)

def make_fake_3d(cover_img):
    """Original simple 3D generator to create the book object."""
    w, h = 600, 900
    cover = cover_img.resize((w, h), Image.Resampling.LANCZOS)
    spine_width = 50
    spine = cover.crop((0, 0, spine_width, h))
    spine = ImageOps.colorize(spine.convert("L"), black="#1a1a1a", white="#555") # Darker spine
    spine = spine.resize((spine_width, h))

    canvas_w = w + spine_width + 50
    canvas_h = h + 50
    book_obj = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    
    # Paste pieces
    book_obj.paste(spine, (0, 20))
    book_obj.paste(cover, (spine_width, 20))
    
    # Draw Pages
    draw = ImageDraw.Draw(book_obj)
    # Right side pages block
    draw.polygon([(spine_width+w, 25), (spine_width+w+20, 40), (spine_width+w+20, 20+h-5), (spine_width+w, 20+h)], fill="#f0f0e0")
    # Bottom pages block
    draw.polygon([(spine_width, 20+h), (spine_width+w, 20+h), (spine_width+w+20, 20+h-5), (spine_width+20, 20+h-5)], fill="#e0e0d0")
    
    return book_obj

# --- THE SCENE COMPOSITOR ---
def composite_scene(user_cover):
    # 1. Setup Canvas (Full HD)
    scene_w, scene_h = 1920, 1080
    scene = Image.new('RGB', (scene_w, scene_h), (20, 15, 10)) # Dark brown base

    # 2. Create Background Elements (Procedural to ensure reliability)
    # Dark Library Background (Top Half)
    bg_layer = Image.new('RGB', (scene_w, scene_h // 2), (10, 5, 5))
    # Add some noise for texture
    noise = Image.effect_noise((scene_w, scene_h // 2), 20).convert('RGB')
    bg_layer = ImageChops.multiply(bg_layer, noise)
    bg_layer = bg_layer.filter(ImageFilter.GaussianBlur(radius=30)) # Heavy blur
    scene.paste(bg_layer, (0,0))

    # Wood Table (Bottom Half)
    table_layer = Image.new('RGB', (scene_w, scene_h // 2 + 100), (60, 40, 20))
    # Add wood grain noise simulation
    wood_noise = Image.effect_noise((scene_w, scene_h // 2 + 100), 40).convert('RGB')
    table_layer = ImageChops.multiply(table_layer, wood_noise)
    scene.paste(table_layer, (0, scene_h // 2 - 50))
    
    # 3. Create and Place the 3D Book
    book = make_fake_3d(user_cover)
    # Scale book down to fit scene nicely
    book_scale = 0.7
    book = book.resize((int(book.width * book_scale), int(book.height * book_scale)), Image.Resampling.LANCZOS)
    
    book_x = (scene_w - book.width) // 2
    book_y = (scene_h - book.height) // 2 + 100

    # 4. Realistic Drop Shadow
    shadow_layer = Image.new('RGBA', scene.size, (0,0,0,0))
    shadow_shape = Image.new('RGBA', (book.width + 40, book.height // 10), (0, 0, 0, 180))
    shadow_layer.paste(shadow_shape, (book_x - 20, book_y + book.height - 30))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=40))
    
    # Composite Shadow and Book onto scene
    scene.paste(shadow_layer, (0,0), mask=shadow_layer)
    scene.paste(book, (book_x, book_y), mask=book)

    # 5. THE DRAMATIC LIGHTING (The "Desk Lamp" Effect)
    # Create a warm, radial spotlight
    # Inner color: Warm yellow/orange, highly transparent
    # Outer color: Dark brown/black, highly opaque (vignette)
    warm_light = (255, 220, 150, 30) 
    dark_vignette = (10, 5, 0, 230)
    
    lighting_gel = create_radial_gradient((scene_w, scene_h), warm_light, dark_vignette)
    
    # Offset the center of the light slightly up to simulate a desk lamp above
    lighting_canvas = Image.new('RGBA', (scene_w, scene_h), dark_vignette)
    lighting_canvas.paste(lighting_gel, (0, -200))

    # Final Composite: Overlay the lighting gel onto the scene
    final_scene = Image.alpha_composite(scene.convert('RGBA'), lighting_canvas)
    
    return final_scene

# --- APP INTERFACE ---
uploaded_file = st.file_uploader("Upload Cover (JPG/PNG)", type=['jpg','png','jpeg'])

if uploaded_file:
    with st.spinner("Compositing Scene... Does your computer smell like mahogany and old paper?"):
        image = Image.open(uploaded_file)
        result = composite_scene(image)
        
        st.divider()
        st.image(result, caption="Dramatic Library Render", use_container_width=True)
        
        # Download Button
        buf = io.BytesIO()
        result.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="⬇️ Download High-Res Scene",
            data=byte_im,
            file_name="library_mockup.png",
            mime="image/png"
        )
        
        st.success("✨ Render Complete!")
        st.markdown("### 💡 The book looks great. Now let the AI write it.")
        st.markdown(f"[**👉 Get Rhythm Logic GPS**](https://rhythm-logic-live.streamlit.app/)")