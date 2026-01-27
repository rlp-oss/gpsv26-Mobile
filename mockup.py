import streamlit as st
from PIL import Image, ImageOps, ImageDraw
import numpy as np

st.set_page_config(page_title="3D Book Generator", page_icon="📚", layout="centered")

st.title("📚 Free 3D Book Mockup")
st.markdown("Upload your flat cover, get a professional 3D render instantly.")

def make_3d_book(cover_img):
    # 1. Resize cover to standard book ratio (6x9 roughly)
    w, h = 600, 900
    cover = cover_img.resize((w, h), Image.Resampling.LANCZOS)
    
    # 2. Create the "Spine" (Just a darkened slice of the cover)
    spine_width = 40
    spine = cover.crop((0, 0, spine_width, h))
    spine = ImageOps.colorize(spine.convert("L"), black="#222", white="#666") # Darken it
    spine = spine.resize((spine_width, h))

    # 3. Create the Canvas (Transparent)
    # We will skew the cover to look 3D
    canvas_w = w + 100
    canvas_h = h + 100
    output = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    
    # 4. Perspective Math (The "Fake 3D" Magic)
    # We are going to paste the spine on the left, and the cover slightly to the right
    # Note: True perspective warp requires CV2, but PIL can do a simple shear/paste
    
    # Draw Shadow
    shadow = Image.new('RGBA', (w + 20, h), (0, 0, 0, 100))
    # output.paste(shadow, (60, 50), mask=shadow)
    
    # Paste Spine
    output.paste(spine, (20, 50))
    
    # Paste Cover
    output.paste(cover, (60, 50))
    
    # Draw "Page Edges" (White block at bottom/right)
    draw = ImageDraw.Draw(output)
    # Right side pages
    draw.polygon([(60+w, 55), (60+w+15, 65), (60+w+15, 50+h-10), (60+w, 50+h)], fill="#eee")
    # Bottom pages
    draw.polygon([(60, 50+h), (60+w, 50+h), (60+w+15, 50+h-10), (75, 50+h-10)], fill="#ddd")

    return output

# --- APP INTERFACE ---
uploaded_file = st.file_uploader("Upload Cover (JPG/PNG)", type=['jpg','png','jpeg'])

if uploaded_file:
    with st.spinner("Rendering 3D Model..."):
        image = Image.open(uploaded_file)
        result = make_3d_book(image)
        
        st.divider()
        st.image(result, caption="Your 3D Mockup", use_container_width=False)
        
        # Download Button
        import io
        buf = io.BytesIO()
        result.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="⬇️ Download 3D PNG (Transparent)",
            data=byte_im,
            file_name="3d_mockup.png",
            mime="image/png"
        )
        
        st.success("✨ Render Complete!")
        st.markdown("### Want to write the book inside?")
        st.markdown(f"[**Get Rhythm Logic GPS**](https://rhythm-logic-live.streamlit.app/)")