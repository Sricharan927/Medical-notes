import streamlit as st
import easyocr
import pandas as pd
import io
import asyncio
import sys
from PIL import Image

# Fix Windows event loop issue
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Initialize EasyOCR
reader = easyocr.Reader(['en'], gpu=False)

# Streamlit UI
st.title("📝 Handwritten Medical Notes OCR")
st.write("Upload an image of a handwritten prescription, and we'll extract the text for you.")

# Initialize session state
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = None
if "df" not in st.session_state:
    st.session_state.df = None
if "processing_done" not in st.session_state:
    st.session_state.processing_done = False

# File Upload
uploaded_file = st.file_uploader("Upload an image (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.session_state.uploaded_file = uploaded_file

# Process image
if st.session_state.uploaded_file and not st.session_state.processing_done:
    image = Image.open(st.session_state.uploaded_file)
    image.thumbnail((800, 800))
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Convert image to bytes for OCR
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")

    # Perform OCR
    with st.spinner("Extracting text... ⏳"):
        text = reader.readtext(img_bytes.getvalue(), detail=0)
        extracted_text = " ".join(text)

    # Store results in session state
    st.session_state.extracted_text = extracted_text
    st.session_state.df = pd.DataFrame([{"Image": st.session_state.uploaded_file.name, "Extracted Text": extracted_text}])
    st.session_state.processing_done = True

# Show results after processing
if st.session_state.processing_done:
    st.subheader("📝 Extracted Text:")
    st.write(st.session_state.extracted_text)

    # Ask user for next step
    st.subheader("📥 What do you want to do?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Download CSV"):
            st.download_button(
                label="📥 Click to Download",
                data=st.session_state.df.to_csv(index=False).encode(),
                file_name="extracted_text.csv",
                mime="text/csv"
            )
            
            # Clear all session state & restart
            st.session_state.uploaded_file = None
            st.session_state.extracted_text = None
            st.session_state.df = None
            st.session_state.processing_done = False
            st.rerun()  # ✅ Fixed rerun function

    with col2:
        if st.button("❌ No, Start Over"):
            # Clear all session state & restart
            st.session_state.uploaded_file = None
            st.session_state.extracted_text = None
            st.session_state.df = None
            st.session_state.processing_done = False
            st.rerun()  # ✅ Fixed rerun function
