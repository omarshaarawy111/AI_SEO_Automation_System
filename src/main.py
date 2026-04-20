import streamlit as st
import pandas as pd
import threading
import time
from components.footer import render_footer
from auth import authorize
from config import website_options
from automation_utils import run_automation
from streamlit_lottie import st_lottie
import json
import os
from components.screen import system_inti, start_keep_awake, stop_keep_awake

system_inti()

def load_lottie_file(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def convert_df_to_csv(df):
    csv_string = '\ufeff' + df.to_csv(index=False, encoding='utf-8')
    return csv_string.encode('utf-8')

def main():
    authorize()
    st.set_page_config(layout="wide", page_icon='🤖', page_title='SEO Automation App')
    
    if "show_lottie" not in st.session_state:
        st.session_state.show_lottie = True

    if st.session_state.show_lottie:
        lottie_container = st.empty()
        base_dir = os.path.dirname(__file__)
        lottie_path = os.path.join(base_dir, "..", "assets", "Website SEO Audit.json")
        try:
            lottie_animation = load_lottie_file(lottie_path)
            with lottie_container:
                st_lottie(lottie_animation, speed=0.5, loop=False, quality="high", height=600)
            time.sleep(2)
        except Exception as e:
            st.warning(f"Could not load animation: {str(e)}")
        finally:
            lottie_container.empty()
            st.session_state.show_lottie = False
    
    st.title("Welcome to SEO Automation App")

    file_type = st.radio("Select approach to work:", ["Excel/CSV", "Images", "No file upload"])
    
    # Initialize variables
    uploaded_file = None
    images_uploaded = None
    df = None
    
    # For "No file upload" - show everything immediately
    if file_type == "No file upload":
        # Show credentials section immediately
        st.title("Enter Login Credentials and Task Details")
        
        col1, col2, col3 = st.columns([3, 1.5, 2])
        with col1:
            selected_website = st.selectbox("Website", list(website_options.keys()))
            website_name = website_options[selected_website]
        show_no_lang = selected_website in ["Nestlé for Healthier Kids"]
        with col2:
            if not show_no_lang:
                if selected_website in ["Nestlé Professional"]:
                    website_lang = st.selectbox("Website Language", ["Arabic", "English", "French"])
                else:
                    website_lang = st.selectbox("Website Language", ["Arabic", "English"])     
            else:
                website_lang = 'None'
        with col3:
            task_type = st.selectbox("Task type", ["Fix Redirects Status Code"])
    
        # Define all flags before using them
        show_shield = selected_website in ["Kitkat", "My Child Nutrition", "Purina"]
        show_nestle_mena = selected_website in ["Nestlé Mena"]
        show_nestle_family = selected_website in ["Nestlé Family"]
        otp = selected_website in ["Baby and Me", "Family Nes", "Nestlé Mena"]

        # User login
        if otp:
            col1, col2, col3 = st.columns([4, 3.5, 2])
            with col1:
                username = st.text_input("Username", placeholder="")
            with col2:
                password = st.text_input("Password", placeholder="", type="password")
            with col3:
                otp_code = st.text_input(
                    "OTP", 
                    placeholder="Make sure the expiration > 25 seconds.",
                    max_chars=6,
                    key="otp_input"
                )
                if otp_code:
                    if not otp_code.isdigit() or len(otp_code) != 6:
                        st.error("❌ OTP must be exactly 6 digits (0-9)!")
                        
        else:     
            col1, col2, col3 = st.columns([4, 3.5, 2])
            with col1:
                username = st.text_input("Username", placeholder="")
            with col2:
                password = st.text_input("Password", placeholder="", type="password")
            otp_code = None   

        # Shield login
        if show_shield:
            col1, col2, col3 = st.columns([4, 3.5, 2])
            with col1:
                shield_username = st.text_input("Shield Username")
            with col2:
                shield_password = st.text_input("Shield Password", type="password")
        else:
            shield_username = None
            shield_password = None

        progress_bar = st.progress(0)
        status_text = st.empty()
        progress_text = st.empty()

        button_col = st.columns([4, 1, 4])[1]
        with button_col:
            automate_button = st.button("Automate 🪄")

        if automate_button:      
            try:
                # Start the keep-awake thread
                start_keep_awake()
                
                # Create an empty DataFrame for "Fix Redirects Status Code" task
                # This prevents NoneType errors in run_automation
                df_for_task = pd.DataFrame()  # Empty DataFrame for redirect fix task
                
                if otp_code is not None:
                    if otp_code.isdigit() and len(otp_code) == 6:
                        run_automation(
                            df_for_task,  # Use empty DataFrame instead of None
                            None,  # No images for this task
                            website_name,
                            website_lang,
                            task_type,  # This will be "Fix Redirects Status Code"
                            username,
                            password,
                            otp_code,
                            shield_username,
                            shield_password,
                            show_shield,
                            show_nestle_mena,
                            show_nestle_family,
                            otp,
                            show_no_lang,
                            progress_bar,
                            status_text,
                            progress_text
                        )
                        render_footer()
                    else:
                        st.error("❌ OTP must be exactly 6 digits (0-9)!")
                else:
                    run_automation(
                        df_for_task,  # Use empty DataFrame instead of None
                        None,  # No images for this task
                        website_name,
                        website_lang,
                        task_type,  # This will be "Fix Redirects Status Code"
                        username,
                        password,
                        otp_code,
                        shield_username,
                        shield_password,
                        show_shield,
                        show_nestle_mena,
                        show_nestle_family,
                        otp,
                        show_no_lang,
                        progress_bar,
                        status_text,
                        progress_text
                    )
                    render_footer()

            except Exception as e:
                st.error(f"❌ Automation has been stopped due to fatal error: {str(e)}")
            finally:
                # Stop the keep-awake thread
                stop_keep_awake()
                
        render_footer()
        return  # Stop execution here for "No file upload"
    
    # For Excel/CSV option
    elif file_type == "Excel/CSV":
        uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["xlsx", "csv"])
        images_uploaded = None

        if uploaded_file is None:
            # Show template and download button only
            template_headers = [
                "URL",
                "H1",
                "New URL Structure",
                "Meta Title", 
                "Meta Description",
                "URL Redirection"
            ]
            template_data = [
                [ 
                    "Orginal URL",
                    "Add H1",
                    "Updating URL alias",
                    "Update meta title",
                    "Update meta Description",
                    "Create redirection route"  
                ]
            ]
            st.markdown(
                "<h3 style='text-align: center;'>Template of file</h3>",
                unsafe_allow_html=True
            )           
            template_df = pd.DataFrame(template_data, columns=template_headers)
            template_df.index = ["Explaination"]
            st.dataframe(template_df,use_container_width=True)
            
            csv = convert_df_to_csv(template_df)

            st.download_button(
                label="Download Template ",
                data=csv,
                file_name='Template_File.csv',
                mime='text/csv',
            )

            st.warning("Please upload a file to proceed.")
            render_footer()
            return  # Stop here until file is uploaded
            
        else:
            # File uploaded - process it
            try:
                if uploaded_file.name.endswith('.csv'):
                    try:
                        df = pd.read_csv(uploaded_file, encoding='utf-8')
                    except UnicodeDecodeError:
                        try:
                            uploaded_file.seek(0)  
                            df = pd.read_csv(uploaded_file, encoding='latin-1')
                        except UnicodeDecodeError:
                            try:
                                uploaded_file.seek(0)
                                df = pd.read_csv(uploaded_file, encoding='utf-16')
                            except:
                                uploaded_file.seek(0)
                                df = pd.read_csv(uploaded_file, encoding='latin-1', errors='ignore')
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.success(f"Successfully uploaded file with {len(df)} total records!")     
                
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                st.info("Please try downloading the template again or ensure your file is in the correct format.")
                render_footer()
                return
    
    # For Images option
    else:  # file_type == "Images"
        images_uploaded = st.file_uploader("Upload images", type=["jpg", "jpeg", "png", "gif"], accept_multiple_files=True)
        uploaded_file = None
        
        if images_uploaded is None or len(images_uploaded) == 0:
            st.warning("Please upload images to proceed.")
            render_footer()
            return
        else:
            st.success(f"Successfully loaded {len(images_uploaded)} images for upload!")
    
    # Show credentials section ONLY if Excel/CSV file is uploaded OR Images are uploaded
    if uploaded_file is not None or (images_uploaded and len(images_uploaded) > 0):
        if uploaded_file:
            show_data = st.checkbox('Show Data', False, key=100)
            if show_data:
                st.dataframe(df)
            st.title("Enter Login Credentials and Task Details")
        else:
            st.title("Enter Login Credentials")

        col1, col2, col3 = st.columns([3, 1.5, 2])
        with col1:
            selected_website = st.selectbox("Website", list(website_options.keys()))
            website_name = website_options[selected_website]
        show_no_lang = selected_website in ["Nestlé for Healthier Kids"]
        with col2:
            if uploaded_file:  # Only show language selection for Excel/CSV tasks
                if not show_no_lang:
                    if selected_website in ["Nestlé Professional"]:
                        website_lang = st.selectbox("Website Language", ["Arabic", "English", "French"])
                    else:
                        website_lang = st.selectbox("Website Language", ["Arabic", "English"])     
                else:
                    website_lang = 'None'
            else:  # For image uploads
                if not show_no_lang:
                    if selected_website in ["Nestlé Professional"]:
                        website_lang = st.selectbox("Website Language", ["Arabic", "English", "French"])
                    else:
                        website_lang = st.selectbox("Website Language", ["Arabic", "English"])     
                else:
                    website_lang = 'None'
        with col3:
            if uploaded_file:
                task_type = st.selectbox("Task type", ["Add H1", "Meta title", "Meta description", "Meta title + description","Add H1 + meta title + description", "URL update", "All", "URL redirection"])
            else:
                task_type = st.selectbox("Task type", ["Upload images with alt text"])

        # Define all flags before using them
        show_shield = selected_website in ["Kitkat", "My Child Nutrition", "Purina"]
        show_nestle_mena = selected_website in ["Nestlé Mena"]
        show_nestle_family = selected_website in ["Nestlé Family"]
        otp = selected_website in ["Baby and Me", "Family Nes", "Nestlé Mena"]

        # User login
        if otp:
            col1, col2, col3 = st.columns([4, 3.5, 2])
            with col1:
                username = st.text_input("Username", placeholder="")
            with col2:
                password = st.text_input("Password", placeholder="", type="password")
            with col3:
                otp_code = st.text_input(
                    "OTP", 
                    placeholder="Make sure the expiration > 25 seconds.",
                    max_chars=6,
                    key="otp_input"
                )
                if otp_code:
                    if not otp_code.isdigit() or len(otp_code) != 6:
                        st.error("❌ OTP must be exactly 6 digits (0-9)!")
                        
        else:     
            col1, col2, col3 = st.columns([4, 3.5, 2])
            with col1:
                username = st.text_input("Username", placeholder="")
            with col2:
                password = st.text_input("Password", placeholder="", type="password")
            otp_code = None   

        # Shield login
        if show_shield:
            col1, col2, col3 = st.columns([4, 3.5, 2])
            with col1:
                shield_username = st.text_input("Shield Username")
            with col2:
                shield_password = st.text_input("Shield Password", type="password")
        else:
            shield_username = None
            shield_password = None

        progress_bar = st.progress(0)
        status_text = st.empty()
        progress_text = st.empty()

        button_col = st.columns([4, 1, 4])[1]
        with button_col:
            automate_button = st.button("Automate 🪄")

        if automate_button:      
            try:
                # Start the keep-awake thread
                start_keep_awake()
                
                if otp_code is not None:
                    if otp_code.isdigit() and len(otp_code) == 6:
                        run_automation(
                            df if uploaded_file else None,
                            images_uploaded,
                            website_name,
                            website_lang,
                            task_type,
                            username,
                            password,
                            otp_code,
                            shield_username,
                            shield_password,
                            show_shield,
                            show_nestle_mena,
                            show_nestle_family,
                            otp,
                            show_no_lang,
                            progress_bar,
                            status_text,
                            progress_text
                        )
                        render_footer()
                    else:
                        st.error("❌ OTP must be exactly 6 digits (0-9)!")
                else:
                    run_automation(
                        df if uploaded_file else None,
                        images_uploaded,
                        website_name,
                        website_lang,
                        task_type,
                        username,
                        password,
                        otp_code,
                        shield_username,
                        shield_password,
                        show_shield,
                        show_nestle_mena,
                        show_nestle_family,
                        otp,
                        show_no_lang,
                        progress_bar,
                        status_text,
                        progress_text
                    )
                    render_footer()

            except Exception as e:
                st.error(f"❌ Automation has been stopped due to fatal error: {str(e)}")
            finally:
                # Stop the keep-awake thread
                stop_keep_awake()
    
    render_footer()
    
if __name__ == "__main__":  
    main()