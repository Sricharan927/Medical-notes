import streamlit as st
import easyocr
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import io
import asyncio
import sys

# Fix for "no running event loop" error in Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Initialize EasyOCR
reader = easyocr.Reader(['en'])

# Streamlit UI
st.title("📝 Handwritten Medical Notes OCR")
st.write("Upload an image of a handwritten prescription, and we'll extract the text for you.")

# Initialize session state
if "processed" not in st.session_state:
    st.session_state.processed = False
if "download_selected" not in st.session_state:
    st.session_state.download_selected = False
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None  # Track uploaded file
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = None  # Store extracted text

# File Upload Button
uploaded_file = st.file_uploader("Upload an image (JPG/PNG)", type=["jpg", "jpeg", "png"])

# Store the uploaded file in session state
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file

# Process the image if uploaded
if st.session_state.uploaded_file is not None and not st.session_state.processed:
    # Display Uploaded Image
    image = Image.open(st.session_state.uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Convert image to bytes for processing
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")

    # Perform OCR
    with st.spinner("Extracting text... ⏳"):
        text = reader.readtext(img_bytes.getvalue(), detail=0)
        extracted_text = " ".join(text)

    # Store extracted text in session state
    st.session_state.extracted_text = extracted_text

    # Show Extracted Text
    st.subheader("📝 Extracted Text:")
    st.write(st.session_state.extracted_text)

    # Convert to CSV
    df = pd.DataFrame([{"Image": st.session_state.uploaded_file.name, "Extracted Text": extracted_text}])
    csv_filename = "extracted_text.csv"
    df.to_csv(csv_filename, index=False)

    # Mark as processed
    st.session_state.processed = True

# Show "Download Results?" buttons only after processing
if st.session_state.processed and not st.session_state.download_selected:
    st.subheader("📥 Do you want to download the results?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, Download CSV"):
            # Provide the CSV download button
            st.download_button(label="📥 Click to Download", data=df.to_csv().encode(), file_name="extracted_text.csv", mime="text/csv")

            # Clear all session state variables and restart
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    with col2:
        if st.button("❌ No, Start Over"):
            # Clear session state and restart
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
