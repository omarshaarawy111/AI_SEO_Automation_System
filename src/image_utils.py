import os
from PIL import Image
import streamlit as st

def convert_to_jpg(image_path):
    """Convert image to JPG format if it's not already"""
    try:
        img = Image.open(image_path)
        if img.format != 'JPEG':
            rgb_img = img.convert('RGB')
            base_name = os.path.splitext(image_path)[0]
            new_path = f"{base_name}.jpg"
            rgb_img.save(new_path, 'JPEG', quality=95)
            if os.path.exists(image_path):
                os.remove(image_path)  # Remove original file
            return new_path
        return image_path
    except Exception as e:
        st.error(f"Error converting image: {str(e)}")
        return image_path

def save_uploaded_images(uploaded_files):
    downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
    os.makedirs(downloads_dir, exist_ok=True)

    saved_paths = []
    for uploaded_file in uploaded_files:
        try:
            # Save the original file first
            temp_path = os.path.join(downloads_dir, uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Convert to JPG if needed
            final_path = convert_to_jpg(temp_path)
            saved_paths.append(final_path)
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
    return saved_paths