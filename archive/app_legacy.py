import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import streamlit as st
import re
import os
from PIL import Image
import requests
from io import BytesIO
from pathlib import Path
import os
import sys


def authorize():
    user_domain = os.environ.get("USERDOMAIN", "").upper()
    ALLOWED_DOMAINS = ["NESTLE"]

    if user_domain not in ALLOWED_DOMAINS:
        st.error(f"🚫 Access denied. Unauthorized User")
        st.stop() 

def get_base_url(website_name, lang):
    base = website_name.rstrip('/')
    
    if '/en/' in base:
        base = base.split('/en/')[0]
    elif '/ar/' in base:
        base = base.split('/ar/')[0]
    elif base.endswith('/en') or base.endswith('/ar'):
        base = base[:-3]

    else:
        if 'pantheonsite.io' in base:
            base = base.split('.io')[0] +'.io'
        else:
            base = base.split('.com')[0] +'.com'
        return base.rstrip('/')        
    
    return base.rstrip('/')

def slugify_url(text, lang):
    """Construct proper URL path with correct language prefix"""
    url = str(text).strip()
    
    if 'pantheonsite.io' in url:
        url = url.split('.io')[-1]
    else:
        url = url.split('.com')[-1]
    
    if url.startswith('/en/') or url.startswith('/ar/'):
        url = url[3:]
        url = url.strip('/')
        return f'/{lang[:2].lower()}/{url}' if url else f'/{lang[:2].lower()}'
    else :
        url = url.strip('/')
        return f'/{url}'

def slugify_alias(text, lang, redirection=False):
    """Extract the path without any language prefix or domain"""
    alias = str(text).strip()
        
    if 'pantheonsite.io' in alias:
        alias = alias.split('.io')[-1]
    else:
        alias = alias.split('.com')[-1]

    if not redirection:
        if alias.startswith('/en/') or alias.startswith('/ar/'):
            alias = alias[3:]
            return alias.strip('/')
        else :
            return alias.strip('/')
    else:
        return alias.strip('/')


def save_uploaded_images(uploaded_files):
    """Save uploaded images to downloads directory"""
    downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
    os.makedirs(downloads_dir, exist_ok=True)
    
    saved_paths = []
    for uploaded_file in uploaded_files:
        try:
            # Read image file
            image = Image.open(uploaded_file)
            
            # Save to downloads directory
            save_path = os.path.join(downloads_dir, uploaded_file.name)
            image.save(save_path)
            saved_paths.append(save_path)
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
    
    return saved_paths

if __name__ == "__main__":
    # Authorize user
    authorize()
    st.set_page_config(layout="wide", page_icon='🤖', page_title='SEO Automation App')
    st.title("Welcome to SEO Automation App")

    # File upload section
    file_type = st.radio("Select file type to upload:", ["Excel/CSV", "Images"])
    
    if file_type == "Excel/CSV":
        uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["xlsx", "csv"])
        images_uploaded = None
    else:
        images_uploaded = st.file_uploader("Upload images", type=["jpg", "jpeg", "png", "gif"], accept_multiple_files=True)
        uploaded_file = None

     

    if uploaded_file is not None or (images_uploaded and len(images_uploaded) > 0):
        if uploaded_file:
            st.success("File uploaded successfully!")
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        else:
            st.success(f"{len(images_uploaded)} images uploaded successfully!")
        if uploaded_file:
            st.title("Enter Login Credentials and Task Details")
        else:
            st.title("Enter Login Credentials")   

        # Website and options
        col1, col2, col3 = st.columns([3, 1.5, 2])
        with col1:
            website_options = {
                "Baby and Me": "https://www.bebe.nestle.ma/user/login?admin=123",
                "Kitkat": "https://kitkat2.factory.kitkat.com/user/login",
                "Maggi": "https://live-71956-food-maggi-me.pantheonsite.io/en/user/login",
                "Mom and Me": "https://www.momandme.nestle-mena.com/en/user/login?admin=123",
                "Mom and Me Medical": "https://momandmemedical.nestle-mena.com/user/login?admin=123",
                "My Cancer My Nutrition": "https://live-dig0056055-nestlehealthscience-mcmn-mena.pantheonsite.io/en/user/126?check_logged_in=1",
                "My Child Nutrition": "http://big.nhscbrand.acsitefactory.com/user/login",
                "My Child With CP": "http://mychildwithcpmena.nhscbrand.acsitefactory.com/user/login",
                "Nature's Bounty": "https://live-dig0057429-natures-bounty-uae-united-arab-emirate.pantheonsite.io/user/login",
                "Nconnect": "https://live-dig0076096-nhsc-nhsc-mena.pantheonsite.io/user/login",
                "Nestlé Family": "https://www.nestle-family.com/en/admin-login",
                "Nestlé Mena": "https://me.factory.nestle.com/en/user/login",
                "Nestlé for Healthier Kids": "https://live-73063--nestleforhealthierkids-unitedarabemirates.pantheonsite.io/user/login",
                "Nestlé Goodnes": "https://test-dig0077344-multicategory-multibrand-france.pantheonsite.io/user/login",
                "Nestlé Health Science": "https://live-61547-healthscience-corporate-me.pantheonsite.io/user/login",
                "Nestlé Professionals": "https://www.nestleprofessionalmena.com/ae/en/HrpeJQiz4ta4o9PSB2YkHhR4/login",
                "NIDO": "https://www.nidolove.com/admin-login",
                "Purina": "https://live-dig0030543-petcare-purinattt-arabia.pantheonsite.io/user/login",
                "Starbucks": "https://live-dig0048100-nestleprofessional-starbucks-uae.pantheonsite.io/en/user/login",
                "Vital protiens": "https://live-dig0054909-nhs-vitalproteins-mena.pantheonsite.io/en/user/login",
                "Wyeth Nutrition Parenting Community": "https://parentingcommunity.wyethnutrition.com/user/login?admin=123"
            }

            selected_website = st.selectbox("Website", list(website_options.keys()))
            website_name = website_options[selected_website]
        if selected_website in ["Nestlé for Healthier Kids"]:
            show_no_lang = True
        else :
            show_no_lang = False    
                
        with col2:
            if not show_no_lang:
                website_lang = st.selectbox("Website Language", ["Arabic", "English"])
            else :
                website_lang = 'None'   
        with col3:
            if uploaded_file:
                task_type = st.selectbox("Task type", ["Meta title", "Meta description", "Meta title + description", "URL update", "All", "URL redirection"])
            else:
                task_type = st.selectbox("Task type", ["Upload images with alt text"])

        if selected_website in ["Kitkat", "My Child Nutrition", "Purina"]:
            show_shield = True
        else:
            show_shield = False  

        if selected_website in ["Nestlé Mena"]:
            show_nestle_mena = True
        else:
            show_nestle_mena = False 

        if  selected_website in ["Nestlé Family"]  :
            show_nestle_family = True
        else:
            show_nestle_family = False   

        if selected_website in ["Baby and Me", "Mom and Me", "Nestlé Mena"]:    
            otp = True
        else:
            otp = False   

        # User login
        if otp:
            col1, col2, col3 = st.columns([4, 3.5, 2])
            with col1:
                username = st.text_input("Username", placeholder="")
            with col2:
                password = st.text_input("Password", placeholder="", type="password")      
            with col3:
                otp_code = st.text_input("OTP", placeholder="Make sure the expiration time bigger than 25 seconds.")
        else:
            col1, col2, col3 = st.columns([4, 3.5, 2])
            with col1:
                username = st.text_input("Username", placeholder="")
            with col2:
                password = st.text_input("Password", placeholder="", type="password")

        # Shield login
        if show_shield:
            col1, col2, col3 = st.columns([4, 3.5, 2])
            with col1:
                shield_username = st.text_input("Shield Username")           
            with col2:
                shield_password = st.text_input("Shield Password", type="password")
   
        # Initialize progress bar and status text
        progress_bar = st.progress(0)
        status_text = st.empty()
        progress_text = st.empty()  # For displaying percentage
        
        # Center the button
        button_col = st.columns([4, 1, 4])[1]
        with button_col:
            automate_button = st.button("Automate 🚀")

        if automate_button:
            base_url = get_base_url(website_name, website_lang)
            st.success(f"✅ Starting automation for: {base_url} ({website_lang}, {task_type})")

            try:
                driver = webdriver.Chrome()
                wait = WebDriverWait(driver, 20)
                login_url = website_name.strip()

                # Handle shield
                if show_shield:
                    if login_url.startswith("http://"):
                        login_url = login_url.replace("http://", f"http://{shield_username}:{shield_password}@")
                    elif login_url.startswith("https://"):
                        login_url = login_url.replace("https://", f"https://{shield_username}:{shield_password}@")
                    st.info(f"Using login URL: {login_url}")
                    driver.get(login_url)
                elif show_nestle_mena:  
                    driver.get(login_url)
                    st.info(f"Using login URL: {login_url}")
                    time.sleep(8)
                elif show_nestle_family:  
                    driver.get(login_url)  
                    st.info(f"Using login URL: {login_url}")
                else:    
                    st.info(f"Using login URL: {login_url}")
                    driver.get(login_url)
                
                # Accept cookies if present
                try:
                    cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
                    cookie_btn.click()
                except:
                    pass  

                if show_nestle_family :
                    username_field = wait.until(EC.presence_of_element_located((By.ID, "edit-name--2")))
                    username_field.clear()
                    username_field.send_keys(username)
                    password_field = wait.until(EC.presence_of_element_located((By.ID, "edit-pass--3")))
                    password_field.clear()
                    password_field.send_keys(password)
                    time.sleep(15)
                    submit_button = wait.until(EC.element_to_be_clickable((By.ID, "edit-actions--3")))
                    submit_button.click()
                    time.sleep(3)
                else :        
                    if not otp:    
                        # Wait for and fill login form
                        try: 
                            username_field = wait.until(EC.presence_of_element_located((By.ID, "edit-name")))
                            username_field.clear()
                            username_field.send_keys(username)
                            password_field = wait.until(EC.presence_of_element_located((By.ID, "edit-pass")))
                            password_field.clear()
                            password_field.send_keys(password)
                            time.sleep(3)
                            submit_button = wait.until(EC.element_to_be_clickable((By.ID, "edit-submit")))
                            submit_button.click()
                            time.sleep(3)
                        except Exception as e:
                            st.error(f"❌ Error during login: {str(e)}")
                            if len(driver.window_handles) > 1:
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                    else:
                        # Wait for and fill login form and otp
                        try: 
                            username_field = wait.until(EC.presence_of_element_located((By.ID, "edit-name")))
                            username_field.clear()
                            username_field.send_keys(username)
                            password_field = wait.until(EC.presence_of_element_located((By.ID, "edit-pass")))
                            password_field.clear()
                            password_field.send_keys(password)
                            time.sleep(3)
                            submit_button = wait.until(EC.element_to_be_clickable((By.ID, "edit-submit")))
                            submit_button.click()
                            otp_field = wait.until(EC.presence_of_element_located((By.ID, "edit-code")))
                            otp_field.clear()
                            otp_field.send_keys(otp_code)
                            verify_button = wait.until(EC.element_to_be_clickable((By.ID, "edit-login")))
                            verify_button.click()
                            time.sleep(3)
                        except Exception as e:
                            st.error(f"❌ Error during login: {str(e)}")
                            if len(driver.window_handles) > 1:
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])   

                # Handle image upload task
                if task_type == "Upload images with alt text":
                    # Save uploaded images to downloads folder
                    image_paths = save_uploaded_images(images_uploaded)
                    st.info(f"Saved {len(image_paths)} images to downloads folder")
                    
                    # Initialize progress
                    total_images = len(image_paths)
                    progress_increment = 100 / total_images if total_images > 0 else 0
                    current_progress = 0
                    
                    # Go to image upload page                   
                    for i, image_path in enumerate(image_paths):
                        try:
                            if show_no_lang:
                                upload_url = f"{base_url}/media/add/image"
                            else :
                                upload_url = f"{base_url}/en/media/add/image"
                            driver.execute_script("window.open('');")
                            driver.switch_to.window(driver.window_handles[1])
                            driver.get(upload_url)
                            alt_texts = {os.path.basename(path): os.path.basename(path).split('.')[0] for path in image_paths}

                            # Find file upload input
                            file_input = wait.until(EC.presence_of_element_located((
                                By.XPATH, "//input[@type='file' and @accept='image/*']"
                            )))
                            
                            # Upload the image
                            file_input.send_keys(image_path)
                            status_text.text(f"Uploading {os.path.basename(image_path)}... ({i+1}/{total_images})")
                            current_progress += progress_increment * 0.3
                            progress_bar.progress(int(current_progress)/100)
                            progress_text.text(f"Progress: {int(current_progress)}%")
                            time.sleep(3)
                            
                            # Fill in name field
                            image_name = os.path.basename(image_path).split('.')[0]
                            name_field = wait.until(EC.presence_of_element_located((By.ID, 'edit-name-0-value')))
                            name_field.clear()
                            name_field.send_keys(image_name)
                            
                            # Fill in alt text
                            alt_text = alt_texts[os.path.basename(image_path)]
                            alt_field = wait.until(EC.presence_of_element_located((
                                By.XPATH, "//input[contains(@id, 'edit-field-media-image-0-alt')]"
                            )))
                            alt_field.clear()
                            alt_field.send_keys(alt_text)
                            current_progress += progress_increment * 0.3
                            progress_bar.progress(int(current_progress)/100)
                            progress_text.text(f"Progress: {int(current_progress)}%")
                            
                            # Save the image   
                            save_button = wait.until(EC.element_to_be_clickable((
                                By.XPATH, "//input[@type='submit' and @value='Save']"
                            )))
                            save_button.click()
                            
                            # Close current tab and switch back to main window
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])

                            st.success(f"✅ Successfully uploaded and added alt text for {os.path.basename(image_path)}")
                            current_progress += progress_increment * 0.4
                            progress_bar.progress(int(current_progress)/100)
                            progress_text.text(f"Progress: {int(current_progress)}%")
                            time.sleep(2)
                            
                        except Exception as e:
                            st.error(f"❌ Error processing {os.path.basename(image_path)}: {str(e)}")
                            if len(driver.window_handles) > 1:
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                            current_progress += progress_increment
                            progress_bar.progress(int(current_progress)/100)
                            progress_text.text(f"Progress: {int(current_progress)}%")
                            continue
                    
                    status_text.text("✅ Image upload completed!")
                    progress_text.text("Progress: 100%")
                    progress_bar.progress(100)
                    st.markdown("📦 End of automation process!")
                
                # Handle Other tasks
                elif task_type != "URL Redirection":
                    total_rows = len(df)
                    progress_increment = 100 / total_rows if total_rows > 0 else 0
                    current_progress = 0
                    
                    for index, row in df.iterrows():
                        try:
                            original_url = row['URL'].strip()
                            url_path = slugify_url(original_url, website_lang)
                            if '/en' not in base_url and '/ar' not in base_url:
                                base_url = get_base_url(base_url, website_lang)
                            full_url = f"{base_url}{url_path}"
                            
                            # Update progress
                            status_text.text(f"Processing {index+1}/{total_rows}: {original_url}")
                            current_progress += progress_increment * 0.2
                            progress_bar.progress(int(current_progress)/100)
                            progress_text.text(f"Progress: {int(current_progress)}%")
                            
                            # Open in new tab
                            driver.execute_script("window.open('');")
                            driver.switch_to.window(driver.window_handles[1])
                            driver.get(full_url)
                            
                            # Task button label based on language
                            if website_lang == "Arabic":
                                try:
                                    task_button = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[text()='المهام']")))
                                except:
                                    task_button = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[text()='Tasks']")))
                                task_button.click()
                            else:
                                task_button = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[text()='Tasks']")))
                                task_button.click()   

                            # Edit button xpath logic
                            if not show_no_lang:
                                if website_lang == "Arabic":
                                    node_path = '/ar/node/' 
                                else: 
                                    node_path = '/en/node/'
                                edit_button = wait.until(EC.element_to_be_clickable((
                                    By.XPATH, f"//a[contains(@href, '{node_path}') and contains(@href, '/edit') and contains(@class, 'moderation-sidebar-link')]"
                                )))
                            else:
                                node_path = '/node/'
                                edit_button = wait.until(EC.element_to_be_clickable((
                                    By.XPATH, f"//a[contains(@href, '{node_path}') and contains(@href, '/edit') and contains(@class, 'moderation-sidebar-link')]"
                                )))    
                            edit_button.click()
                            current_progress += progress_increment * 0.2
                            progress_bar.progress(int(current_progress)/100)
                            progress_text.text(f"Progress: {int(current_progress)}%")

                            if task_type == "URL update":
                                new_alias = slugify_alias(row['New URL Structure'], website_lang)
                                alias_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-path-0-alias')))
                                alias_input.clear()
                                alias_input.send_keys(f'/{new_alias}')
                                if not show_no_lang:
                                    st.write(f"✅ [{index+1}] Updated alias: {full_url} → {base_url}/{website_lang[:2].lower()}/{new_alias}")
                                else:
                                    st.write(f"✅ [{index+1}] Updated alias: {full_url} → {base_url}{new_alias}")

                            elif task_type == "Meta title":
                                meta_title = row['Meta Title']                                                            
                                tab = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, "summary[aria-controls='edit-field-ln-n-meta-tags-0']"))
                                )
                                tab.click()
                                time.sleep(1)
                                try :
                                    title_input  = wait.until(EC.presence_of_element_located((By.ID, 'edit-field-ln-n-meta-tags-0-basic-title')))
                                except:
                                    title_input  = wait.until(EC.presence_of_element_located((By.ID, 'edit-field-meta-tags-0-basic-title')))
                                title_input.clear()
                                title_input.send_keys(meta_title)
                                st.write(f"✅ [{index+1}] Updated meta title: {full_url}")

                            elif task_type == "Meta description":
                                meta_desc = row['Meta Description']
                                tab = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, "summary[aria-controls='edit-field-ln-n-meta-tags-0']"))
                                )
                                tab.click()
                                time.sleep(1)
                                try :
                                    desc_input  = wait.until(EC.presence_of_element_located((By.ID, 'edit-field-ln-n-meta-tags-0-basic-description')))
                                except:
                                    desc_input  = wait.until(EC.presence_of_element_located((By.ID, 'edit-field-meta-tags-0-basic-description')))
                                desc_input.clear()
                                desc_input.send_keys(meta_desc)
                                st.write(f"✅ [{index+1}] Updated meta description: {full_url}")

                            elif task_type == "Meta title + description":
                                meta_title = row['Meta Title']
                                meta_desc = row['Meta Description']
                                tab = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, "summary[aria-controls='edit-field-ln-n-meta-tags-0']"))
                                )
                                tab.click()
                                time.sleep(1)
                                try :
                                    title_input  = wait.until(EC.presence_of_element_located((By.ID, 'edit-field-ln-n-meta-tags-0-basic-title')))
                                except:
                                    title_input  = wait.until(EC.presence_of_element_located((By.ID, 'edit-field-meta-tags-0-basic-title')))
                                                               
                                tab = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, "summary[aria-controls='edit-field-ln-n-meta-tags-0']"))
                                )
                                tab.click()
                                time.sleep(1)
                                try :
                                    desc_input  = wait.until(EC.presence_of_element_located((By.ID, 'edit-field-ln-n-meta-tags-0-basic-description')))
                                except:
                                    desc_input  = wait.until(EC.presence_of_element_located((By.ID, 'edit-field-meta-tags-0-basic-description')))
                                title_input.clear()
                                title_input.send_keys(meta_title)
                                desc_input.clear()
                                desc_input.send_keys(meta_desc)
                                st.write(f"✅ [{index+1}] Updated meta title & description: {full_url}")

                            elif task_type == "All":
                                new_alias = slugify_alias(row['New URL Structure'], website_lang)
                                meta_title = row['Meta Title']
                                meta_desc = row['Meta Description']
                                alias_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-path-0-alias')))
                                tab = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, "summary[aria-controls='edit-field-ln-n-meta-tags-0']"))
                                )
                                tab.click()
                                time.sleep(1)
                                try :
                                    title_input  = wait.until(EC.presence_of_element_located((By.ID, 'edit-field-ln-n-meta-tags-0-basic-title')))
                                except:
                                    title_input  = wait.until(EC.presence_of_element_located((By.ID, 'edit-field-meta-tags-0-basic-title')))
                                                               
                                tab = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, "summary[aria-controls='edit-field-ln-n-meta-tags-0']"))
                                )
                                tab.click()
                                time.sleep(1)
                                try :
                                    desc_input  = wait.until(EC.presence_of_element_located((By.ID, 'edit-field-ln-n-meta-tags-0-basic-description')))
                                except:
                                    desc_input  = wait.until(EC.presence_of_element_located((By.ID, 'edit-field-meta-tags-0-basic-description')))
                                alias_input.clear()
                                alias_input.send_keys(f'/{new_alias}')
                                title_input.clear()
                                title_input.send_keys(meta_title)
                                desc_input.clear()
                                desc_input.send_keys(meta_desc)
                                if show_no_lang:
                                    st.write(f"✅ [{index+1}] Updated alias, meta title & description: {base_url}/{website_lang[:2].lower()}/{new_alias}")  
                                else:
                                    st.write(f"✅ [{index+1}] Updated alias, meta title & description: {full_url} → {base_url}/{new_alias}")
                            # Save
                            current_progress += progress_increment * 0.4
                            progress_bar.progress(int(current_progress)/100)
                            progress_text.text(f"Progress: {int(current_progress)}%")
                            save_button = wait.until(EC.element_to_be_clickable((By.ID, "edit-submit")))
                            save_button.click()
                            time.sleep(2)
                            
                            # Close current tab and switch back to main window
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])

                            current_progress += progress_increment * 0.2
                            progress_bar.progress(int(current_progress)/100)
                            progress_text.text(f"Progress: {int(current_progress)}%")
                            status_text.text(f"Completed {index+1}/{total_rows}")

                        except Exception as e:
                            st.error(f"❌ [{index+1}] Error with {original_url}: {str(e)}")
                            if len(driver.window_handles) > 1:
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                            current_progress += progress_increment
                            progress_bar.progress(int(current_progress)/100)
                            progress_text.text(f"Progress: {int(current_progress)}%")
                            continue
                    
                    status_text.text("✅ Automation completed successfully!")
                    progress_text.text("Progress: 100%")
                    progress_bar.progress(100)
                    st.markdown("📦 End of automation process!")
                 
                else:
                    # Handle URL Redirection task    
                    total_rows = len(df)
                    progress_increment = 100 / total_rows if total_rows > 0 else 0
                    current_progress = 0
                    
                    for index, row in df.iterrows():
                        try:
                            original_url = row['URL'].strip()
                            to_url = row['URL Redirection'].strip()
                            
                            # Update progress
                            status_text.text(f"Processing redirection {index+1}/{total_rows}: {original_url}")
                            current_progress += progress_increment * 0.2
                            progress_bar.progress(int(current_progress)/100)
                            progress_text.text(f"Progress: {int(current_progress)}%")
                            
                            redirect_url = base_url+'/admin/config/search/redirect/add'
                            driver.execute_script("window.open('');")
                            driver.switch_to.window(driver.window_handles[1])
                            driver.get(redirect_url)
                            
                            path_url_slug = slugify_alias(original_url, website_lang, redirection=True)
                            path_url_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-redirect-source-0-path')))
                            to_url_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-redirect-redirect-0-uri'))) 
                            path_url_input.send_keys(f'{path_url_slug}')
                            to_url_input.send_keys(f'{to_url}')
                            current_progress += progress_increment * 0.4
                            progress_bar.progress(int(current_progress)/100)
                            progress_text.text(f"Progress: {int(current_progress)}%")
                            time.sleep(1.5)
                            
                            # Save
                            save_redirection_button = wait.until(EC.element_to_be_clickable((By.ID, "edit-submit")))
                            save_redirection_button.click()
                            
                            # Close current tab and switch back to main window
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])

                            st.write(f"✅ [{index+1}] Updated URL redirection: {original_url}")
                            current_progress += progress_increment * 0.4
                            progress_bar.progress(int(current_progress)/100)
                            progress_text.text(f"Progress: {int(current_progress)}%")
                            status_text.text(f"Completed redirection {index+1}/{total_rows}")
                            
                        except Exception as e:
                            st.error(f"❌ [{index+1}] Error with {original_url}: {str(e)}")
                            if len(driver.window_handles) > 1:
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                            current_progress += progress_increment
                            progress_bar.progress(int(current_progress)/100)
                            progress_text.text(f"Progress: {int(current_progress)}%")
                            continue
                    
                    status_text.text("✅ URL redirections completed!")
                    progress_text.text("Progress: 100%")
                    progress_bar.progress(100)
                    st.markdown("📦 End of automation process!")
                  
            except Exception as e:
                st.error(f"❌ Critical error occurred: {str(e)}")
                progress_bar.progress(100)
                progress_text.text("Progress: 100%")
                st.markdown("📦 End of automation process!")

        # Footer
        st.markdown(
                """
                <div style='text-align: center; margin-top: 50px;'>
                    <img src="https://1000logos.net/wp-content/uploads/2017/03/Nestle-Logo.png" alt="Nestlé Logo" width="120" style="margin-bottom: 10px;" />
                    <h4 style='font-size: 22px;'>🚀 Made with ❤️ by the <b>Web & Search Team</b> – NBS Cairo</h4>
                    <h4 style='font-size: 16px;'>📌 Authority : <b>Omar Shaarawy</b> | Version 1.0.0 Beta</h4>
                </div>
                """,
                unsafe_allow_html=True
                ) 
    else:
        st.warning("Please upload a file to proceed.")
