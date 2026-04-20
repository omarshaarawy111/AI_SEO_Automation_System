from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from src.file_utils import get_base_url, slugify_url, slugify_alias
from src.image_utils import save_uploaded_images
from src.config import get_website_name
import streamlit as st
import time
import os
import pandas as pd
import io
import uuid
import platform

# Import pywin32 for Windows-specific window minimization
try:
    import win32gui
    import win32con
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False
    st.warning("pywin32 not installed. Using Selenium's minimize_window() as fallback for browser minimization.")

# Constants for sleep timings
VLIDATE_WAIT = 2 # for verify saving
SHORT_WAIT = 5  # For meta tags and basic tags
LONG_WAIT = 10  # For page loads and edit buttons
SAVE_TIMEOUT = 3  # For save operations
EPOCH_SIZE = 20  # Number of rows per epoch for Nestlé Professional and Nestlé MENA

def format_time(seconds):
    """Convert seconds to a human-readable format (hours, minutes, seconds)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    parts = []
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if secs > 0 or not parts:
        parts.append(f"{secs} second{'s' if secs != 1 else ''}")
    return ", ".join(parts)

def open_sidebar_with_all_methods(driver, timeout=10):
    """
    Try all possible methods to open the sidebar until one succeeds
    Returns True if sidebar was opened, False if all methods failed
    """
    methods = [
        _try_standard_click,
        _try_javascript_click,
        _try_action_chains_click,
        _try_double_click,
        _try_direct_css_manipulation,
        _try_coordinate_click,
        _try_force_sidebar_open
    ]
    
    for method in methods:
        try:
            if method(driver, timeout):
                if _verify_sidebar_open(driver, timeout):
                    return True
        except Exception as e:
            continue
    
    st.warning("All methods failed to open the sidebar")
    return False

def _verify_sidebar_open(driver, timeout):
    """Verify the sidebar is actually visible"""
    try:
        return WebDriverWait(driver, timeout).until(
            lambda d: d.find_element(By.CSS_SELECTOR, "#gin_sidebar").is_displayed() and
                     "is-active" in d.find_element(By.CSS_SELECTOR, "a.meta-sidebar__trigger").get_attribute("class")
        )
    except:
        return False

def _try_standard_click(driver, timeout):
    """Method 1: Standard click with state checks"""
    toggle = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.meta-sidebar__trigger")))
    
    is_expanded = toggle.get_attribute("aria-expanded") == "true"
    is_active = "is-active" in toggle.get_attribute("class")
    title = toggle.get_attribute("title")
    
    if "Hide" not in title or not is_expanded or not is_active:
        toggle.click()
        time.sleep(1)  # Animation time
    return True

def _try_javascript_click(driver, timeout):
    """Method 2: JavaScript click with forced state"""
    driver.execute_script("""
        const toggle = document.querySelector('a.meta-sidebar__trigger');
        toggle.click();
        toggle.setAttribute('aria-expanded', 'true');
        toggle.classList.add('is-active');
        document.getElementById('gin_sidebar').style.display = 'block';
    """)
    time.sleep(1)
    return True

def _try_action_chains_click(driver, timeout):
    """Method 3: Human-like interaction with ActionChains"""
    toggle = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.meta-sidebar__trigger")))
    
    ActionChains(driver)\
        .move_to_element(toggle)\
        .pause(0.5)\
        .click()\
        .perform()
    time.sleep(1)
    return True

def _try_double_click(driver, timeout):
    """Method 4: Double click approach"""
    toggle = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.meta-sidebar__trigger")))
    
    toggle.click()
    time.sleep(0.3)
    toggle.click()
    time.sleep(1)
    return True

def _try_direct_css_manipulation(driver, timeout):
    """Method 5: Direct CSS manipulation"""
    driver.execute_script("""
        document.getElementById('gin_sidebar').style.transform = 'translateX(0)';
        document.getElementById('gin_sidebar').style.visibility = 'visible';
        document.querySelector('a.meta-sidebar__trigger').setAttribute('aria-expanded', 'true');
        document.querySelector('a.meta-sidebar__trigger').classList.add('is-active');
    """)
    time.sleep(1)
    return True

def _try_coordinate_click(driver, timeout):
    """Method 6: Coordinate-based precise click"""
    toggle = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.meta-sidebar__trigger")))
    
    loc = toggle.location
    size = toggle.size
    
    ActionChains(driver)\
        .move_to_element_with_offset(toggle, size['width']/2, size['height']/2)\
        .click()\
        .perform()
    time.sleep(1)
    return True

def _try_force_sidebar_open(driver, timeout):
    """Method 7: Nuclear option - force all possible open states"""
    driver.execute_script("""
        // Force open the sidebar panel
        const sidebar = document.getElementById('gin_sidebar');
        sidebar.style.display = 'block';
        sidebar.style.visibility = 'visible';
        sidebar.style.opacity = '1';
        sidebar.style.transform = 'translateX(0)';
        
        // Force toggle button state
        const toggle = document.querySelector('a.meta-sidebar__trigger');
        toggle.setAttribute('aria-expanded', 'true');
        toggle.classList.add('is-active');
        toggle.setAttribute('title', 'Hide sidebar panel');
        
        // Remove any transition/animation effects
        sidebar.style.transition = 'none';
        sidebar.style.animation = 'none';
    """)
    time.sleep(1)
    return True

def try_open_metatags_dropdown(wait, driver, website_name):
    """
    Enhanced method to open meta tags dropdown handling all cases:
    - Taxonomy pages
    - Nestlé Professional sidebar
    - Non-Nestlé Professional pages
    - Basic tags expansion
    """
    websitename = get_website_name(website_name)
    short_wait = WebDriverWait(driver, SHORT_WAIT)
    
    # Check if URL contains "/taxonomy" for taxonomy flow
    is_taxonomy = "/taxonomy" in driver.current_url
    
    if is_taxonomy:
        # Enhanced taxonomy flow handling
        try:
            # Try both possible meta tags links
            for selector in [
                "a[href='#edit-field-metatags-0']",
                "a[href*='edit-field-meta-tags']"
            ]:
                try:
                    meta_tags_link = short_wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", meta_tags_link)
                    driver.execute_script("arguments[0].click();", meta_tags_link)
                    # Verify meta tags section is accessible
                    short_wait.until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "#edit-field-metatags-0-basic, [id*='edit-field-meta-tags'][id*='basic']")))
                    return True
                except:
                    continue
            raise Exception("No valid meta tags link found")
        except Exception as e:
            st.error(f"Failed to open meta tags section in taxonomy flow: {str(e)}")
            return False
    else:
        # Handle different website types
        if websitename == "Nestlé Professional":
            # Nestlé Professional requires sidebar opening
            if not open_sidebar_with_all_methods(driver, SHORT_WAIT):
                st.error("Failed to open sidebar for Nestlé Professional")
                return False
            
            # Try multiple meta tags selectors
            meta_selectors = [
                "summary[aria-controls='edit-field-meta-tags-0']",
                "summary[aria-controls='edit-field-ln-n-meta-tags-0']",
                "button[aria-controls*='edit-field-meta-tags']",
                "summary.claro-details__summary"
            ]
        else:
            # Generic approach for other sites
            meta_selectors = [
                "summary[aria-controls*='edit-field-meta-tags']",
                "summary[aria-controls*='edit-field-ln-n-meta-tags']",
                "summary.seven-details__summary",
                "summary[role='button'][aria-controls*='meta-tags']",
                "button[aria-expanded][aria-controls*='meta-tags']"
            ]

        # Common field selectors
        meta_title_selectors = [
            "#edit-field-meta-tags-0-basic-title",
            "#edit-field-ln-n-meta-tags-0-basic-title",
            "[id*='edit-field-meta-tags'][id*='title']"
        ]
        
        meta_desc_selectors = [
            "#edit-field-meta-tags-0-basic-description",
            "#edit-field-ln-n-meta-tags-0-basic-description",
            "[id*='edit-field-meta-tags'][id*='description']"
        ]
        
        meta_tags_container_selectors = [
            "#edit-field-meta-tags-0",
            "#edit-field-ln-n-meta-tags-0",
            "[id*='edit-field-meta-tags']"
        ]
        
        basic_tags_selector = "summary[aria-controls*='edit-field'][aria-controls*='meta-tags'][aria-controls*='basic']"

        # Attempt to expand meta tags section
        for selector in meta_selectors:
            try:
                element = short_wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                
                # Toggle if not expanded
                if element.get_attribute("aria-expanded") != "true":
                    driver.execute_script("arguments[0].click();", element)
                
                # Verify expansion
                for container_selector in meta_tags_container_selectors:
                    try:
                        short_wait.until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, container_selector)))
                        # Found visible container, break out
                        break
                    except:
                        continue
                else:
                    # No container found, try next method
                    continue
                    
                # Expand Basic Tags if needed
                try:
                    basic_tags = short_wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, basic_tags_selector)))
                    if basic_tags.get_attribute("aria-expanded") != "true":
                        driver.execute_script("arguments[0].click();", basic_tags)
                except:
                    # Basic tags might already be expanded or not present
                    pass
                    
                # Verify meta title field is accessible
                for title_selector in meta_title_selectors:
                    try:
                        meta_title_field = short_wait.until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, title_selector)))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", meta_title_field)
                        return True
                    except:
                        continue
                        
                # If we got here but no title field, try next method
                continue
                
            except Exception as e:
                continue
                
        return False

def check_for_error_message(driver, wait):
    """Check if an error message is present on the page."""
    try:
        # Check for error messages in multiple languages
        error_selectors = [
            ".messages--error", 
            ".alert-danger", 
            "div[role='alert']",
            "div.error",  # English error
            "div.erreur",  # French error
            "div.خطأ",  # Arabic error
            "div.رسالة-خطأ",  # Arabic error message
            "div[contains(text(), 'error')]",  # English
            "div[contains(text(), 'erreur')]",  # French
            "div[contains(text(), 'خطأ')]",  # Arabic
            "div[contains(text(), 'حفظ')][contains(@class, 'error')]"  # Arabic save error
        ]
        
        for selector in error_selectors:
            try:
                error_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if error_element and error_element.is_displayed():
                    return error_element.text
            except:
                continue
        return None
    except:
        return None

def verify_save_success(driver, wait, original_edit_url):
    """
    Verify save success by checking if '/edit' is no longer in the URL.
    Returns True if successfully saved (no '/edit' in URL), False otherwise.
    
    Args:
        driver: WebDriver instance
        wait: WebDriverWait instance
        original_edit_url: The URL of the edit page before clicking save
    """
    try:
        # Wait for URL to change and no longer contain '/edit'
        def is_edit_page_gone(driver):
            current_url = driver.current_url.split('?')[0]  # Ignore query parameters
            return '/edit' not in current_url
        
        # Wait for URL to change with a reasonable timeout (using existing wait timeout)
        wait.until(is_edit_page_gone)
        return True
        
    except TimeoutException:
        # If we're still on an edit page after timeout
        current_url = driver.current_url.split('?')[0]
        if '/edit' in current_url:
            return False
        
        # Final fallback - check for error messages
        error_message = check_for_error_message(driver, WebDriverWait(driver, 2))
        if error_message:
            return False
            
        # If no error messages and no /edit in URL, assume success
        return True

def click_save_button(driver, wait, website_name, website_lang, is_taxonomy):
    """Enhanced save button click with /edit URL validation"""
    original_edit_url = driver.current_url  # Capture URL before saving
    websitename = get_website_name(website_name)
    
    try:
        if is_taxonomy:
            # Handle taxonomy save buttons in all languages
            save_button_selectors = [
                ("input[value='Save']", "English"),
                ("input[value='Enregistrer']", "French"),
                ("input[value='حفظ']", "Arabic"),
                ("button[data-drupal-selector='edit-submit']", "Generic"),
                ("input[type='submit']", "Generic Submit")
            ]
            
            for selector, _ in save_button_selectors:
                try:
                    save_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            else:
                raise Exception("No save button found for taxonomy")
        else:
            # Handle all possible save button variations for non-taxonomy
            save_button_selectors = [
                "#gin-sticky-edit-submit",
                "#edit-submit",
                "input[value='Save']",
                "input[value='Enregistrer']",
                "input[value='حفظ']",
                "button[data-drupal-selector='edit-submit']",
                "input[type='submit']",
                "button[type='submit']"
            ]
            
            for selector in save_button_selectors:
                try:
                    save_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            else:
                raise Exception("No save button found")
        
        # Scroll to and click the save button
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
        driver.execute_script("arguments[0].click();", save_button)
        
        # Verify success by checking if we're no longer on an edit page
        if verify_save_success(driver, wait, original_edit_url):
            return True
            
        # If verify_save_success returned False, check for error messages
        error_message = check_for_error_message(driver, WebDriverWait(driver, 2))
        if error_message:
            raise Exception(f"Save failed with message: {error_message}")
        else:
            raise Exception("Save operation did not redirect from edit page")
            
    except Exception as e:
        return False


def perform_login(driver, wait, website_name, website_lang, username, password, otp_code, show_shield, shield_username, shield_password, show_nestle_mena, show_nestle_family, otp):
    login_url = website_name.strip()
    try:
        if show_shield:
            if login_url.startswith("http://"):
                login_url = login_url.replace("http://", f"http://{shield_username}:{shield_password}@")
            elif login_url.startswith("https://"):
                login_url = login_url.replace("https://", f"https://{shield_username}:{shield_password}@")
            st.info(f"Using login URL: {login_url}")
            driver.get(login_url)
        elif show_nestle_mena or show_nestle_family:
            driver.get(login_url)
            time.sleep(LONG_WAIT)
            st.info(f"Using login URL: {login_url}")
        else:
            driver.get(login_url)
            st.info(f"Using login URL: {login_url}")

        # Handle cookie consent if present
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#onetrust-accept-btn-handler, .cookie-accept-btn, .accept-cookies")))
            driver.execute_script("arguments[0].click();", cookie_btn)
            time.sleep(1)
        except:
            pass

        # Handle different login forms
        login_success = False
        login_attempts = [
            # Nestlé Family login
            {
                'condition': show_nestle_family,
                'selectors': {
                    'username': "#edit-name--2",
                    'password': "#edit-pass--3",
                    'submit': "#edit-actions--3"
                }
            },
            # Standard Drupal login
            {
                'condition': True,  # Always try
                'selectors': {
                    'username': "#edit-name",
                    'password': "#edit-pass",
                    'submit': "#edit-submit"
                }
            },
            # Generic login form fallback
            {
                'condition': True,
                'selectors': {
                    'username': "input[name='name'], input[name='username']",
                    'password': "input[name='pass'], input[name='password']",
                    'submit': "input[type='submit'], button[type='submit']"
                }
            }
        ]

        for attempt in login_attempts:
            if not attempt['condition']:
                continue
                
            try:
                username_field = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, attempt['selectors']['username'])))
                username_field.clear()
                username_field.send_keys(username)
                
                password_field = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, attempt['selectors']['password'])))
                password_field.clear()
                password_field.send_keys(password)
                
                submit_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, attempt['selectors']['submit'])))
                driver.execute_script("arguments[0].click();", submit_button)
                
                # Check for OTP requirement
                if otp:
                    try:
                        otp_field = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "#edit-code, input[name='code']")))
                        otp_field.clear()
                        otp_field.send_keys(otp_code)
                        
                        verify_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "#edit-login, button[name='op']")))
                        driver.execute_script("arguments[0].click();", verify_button)
                    except:
                        pass
                
                # Verify login success
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "body.logged-in, .toolbar-tray"))
                )
                login_success = True
                break
                
            except Exception as e:
                continue
                
        if not login_success:
            raise Exception("All login methods failed")
            
    except Exception as e:
        st.error(f"❌ Failed to login: {str(e)}")
        raise

def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    
    # Add additional options for better stability
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    #options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)
    
    # Minimize the browser window
    if platform.system() == "Windows" and PYWIN32_AVAILABLE:
        hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    else:
        driver.minimize_window()
    
    return driver

def process_rows(driver, wait, epoch_df, base_url, website_name, website_lang, task_type, show_no_lang, total_rows, progress_bar, status_text, progress_text, progress_increment, current_progress, operation_times, success_count, failures, processed_rows, epoch_idx, total_epochs, use_epochs):
    for index, row in epoch_df.iterrows():
        row_start_time = time.time()
        try:
            if task_type == "URL redirection":
                original_url = row['URL'].strip()
                to_url = row['URL Redirection'].strip()
                status_text.text(f"Processing redirection {index+1}/{total_rows}: {original_url}")
                current_progress[0] = min(current_progress[0] + progress_increment * 0.2, 100)
                progress_bar.progress(int(current_progress[0]))
                progress_text.text(f"Progress: {int(current_progress[0])}%{' (Epoch {}/{})'.format(epoch_idx + 1, total_epochs) if use_epochs else ''}")
                redirect_url = f"{base_url}/admin/config/search/redirect/add"
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(redirect_url)
                path_url_slug = slugify_alias(original_url, redirection=True)
                path_url_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-redirect-source-0-path')))
                to_url_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-redirect-redirect-0-uri')))
                driver.execute_script("arguments[0].value = '';", path_url_input)
                driver.execute_script("arguments[0].value = arguments[1];", path_url_input, f'{path_url_slug}')
                driver.execute_script("arguments[0].value = '';", to_url_input)
                driver.execute_script("arguments[0].value = arguments[1];", to_url_input, f'{to_url}')
                current_progress[0] = min(current_progress[0] + progress_increment * 0.4, 100)
                progress_bar.progress(int(current_progress[0]))
                progress_text.text(f"Progress: {int(current_progress[0])}%{' (Epoch {}/{})'.format(epoch_idx + 1, total_epochs) if use_epochs else ''}")
                if click_save_button(driver, wait, website_name, website_lang, False):
                    row_time = time.time() - row_start_time
                    operation_times.append(row_time)
                    success_count[0] += 1
                    processed_rows.add(index)
                    st.success(f"✅ [{index+1}] Updated URL redirection: {original_url} (Execution time: {format_time(row_time)})")
                else:
                    raise Exception("Failed to save redirection")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                current_progress[0] = min(current_progress[0] + progress_increment * 0.4, 100)
                progress_bar.progress(int(current_progress[0]))
                progress_text.text(f"Progress: {int(current_progress[0])}%{' (Epoch {}/{})'.format(epoch_idx + 1, total_epochs) if use_epochs else ''}")
                status_text.text(f"Completed redirection {index+1}/{total_rows} (Execution time: {format_time(row_time)})")
            else:
                original_url = row['URL'].strip()
                url_path = slugify_url(original_url, website_lang)
                if '/en' not in base_url and '/ar' not in base_url:
                    base_url = get_base_url(base_url)
                full_url = f"{base_url}{url_path}"
                status_text.text(f"Processing {index+1}/{total_rows}: {original_url}")
                current_progress[0] = min(current_progress[0] + progress_increment * 0.2, 100)
                progress_bar.progress(int(current_progress[0]))
                progress_text.text(f"Progress: {int(current_progress[0])}%{' (Epoch {}/{})'.format(epoch_idx + 1, total_epochs) if use_epochs else ''}")
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                try:
                    driver.get(full_url)
                except Exception as e:
                    raise Exception(f"Failed to load page: {str(e)}")
                if show_no_lang:
                    node_path = '/node/' 
                else:
                    if website_lang == "Arabic":
                        node_path = '/ar/node/'
                    elif website_lang == "English":
                        node_path = '/en/node/'
                    elif website_lang == "French":
                        node_path = '/fr/node/' 

                if get_website_name(website_name) in ["Nestlé for Healthier Kids", "Nestlé Professional"]:
                    if website_lang in ["Arabic", "English"]:
                        edit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'nav-link') and contains(text(), 'Edit')]")))
                        driver.execute_script("arguments[0].click();", edit_button)
                    elif website_lang == "French":
                        edit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'nav-link') and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'modifier')]")))
                        driver.execute_script("arguments[0].click();", edit_button)
                else:
                    if not show_no_lang:
                        task_text = "المهام" if website_lang == "Arabic" else "Tasks" if website_lang == "English" else "Tâches" if website_lang == "French" else "Tasks"
                        try:
                            task_button = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[text()='{task_text}']")))
                            driver.execute_script("arguments[0].click();", task_button)
                            if website_lang == "French":
                                edit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'modifier')]")))
                            else:
                                edit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.moderation-sidebar-link.button[href*='edit']")))                            
                                driver.execute_script("arguments[0].click();", edit_button)
                        except Exception as e:
                            raise Exception(f"Failed to access edit page via Tasks button: {str(e)}")
                    else:
                        try:
                            edit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.moderation-sidebar-link.button[href*='edit']")))
                            driver.execute_script("arguments[0].click();", edit_button)
                        except Exception as e:
                            raise Exception(f"Failed to access edit page via link text: {str(e)}")   
                progress_text.text(f"Progress: {int(current_progress[0])}%{' (Epoch {}/{})'.format(epoch_idx + 1, total_epochs) if use_epochs else ''}")
                
                # Check if URL contains "/taxonomy" for meta tags and alias handling
                is_taxonomy = "/taxonomy" in driver.current_url
                
                if task_type == "URL update":
                    try:
                        new_alias = slugify_alias(row['New URL Structure'])
                        if is_taxonomy:
                            alias_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-field-metatags-0-advanced-canonical-url')))
                        else:
                            alias_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-path-0-alias')))
                        driver.execute_script("arguments[0].value = '';", alias_input)
                        driver.execute_script("arguments[0].value = arguments[1];", alias_input, f'/{new_alias}')
                    except Exception as e:
                        raise Exception(f"Failed to update URL alias: {str(e)}")
                    if click_save_button(driver, wait, website_name, website_lang, is_taxonomy):
                        row_time = time.time() - row_start_time
                        operation_times.append(row_time)
                        success_count[0] += 1
                        processed_rows.add(index)
                        st.success(f"✅ [{index+1}] Updated alias: {full_url} → {base_url}/{website_lang[:2].lower()}/{new_alias} (Execution time: {format_time(row_time)})")
                    else:
                        raise Exception("Failed to save URL alias changes")
                elif task_type == "Meta title":
                    meta_title = row['Meta Title']
                    if not try_open_metatags_dropdown(wait, driver, website_name):
                        try:
                            # Try direct URL manipulation for taxonomy
                            if is_taxonomy:
                                driver.get(f"{driver.current_url}#edit-field-metatags-0")
                            else:
                                # Try to force open with JavaScript
                                driver.execute_script("""
                                    document.querySelectorAll('summary[aria-controls*=\"meta-tags\"]').forEach(el => {
                                        if (el.getAttribute('aria-expanded') !== 'true') {
                                            el.click();
                                        }
                                    });
                                    document.querySelectorAll('summary[aria-controls*=\"basic\"]').forEach(el => {
                                        if (el.getAttribute('aria-expanded') !== 'true') {
                                            el.click();
                                        }
                                    });
                                """)
                                time.sleep(1)
                            
                            # Verify we can access fields
                            title_field_present = False
                            for selector in [
                                "#edit-field-metatags-0-basic-title",
                                "#edit-field-ln-n-meta-tags-0-basic-title",
                                "[id*='edit-field-meta-tags'][id*='title']"
                            ]:
                                try:
                                    driver.find_element(By.CSS_SELECTOR, selector)
                                    title_field_present = True
                                    break
                                except:
                                    continue
                                    
                            if not title_field_present:
                                raise Exception("Fallback failed to access meta fields")
                                
                        except Exception as fallback_e:
                            raise Exception(f"Both primary and fallback meta tags methods failed: {str(fallback_e)}")

                    short_wait = WebDriverWait(driver, SHORT_WAIT)
                    title_input = None
                    if is_taxonomy:
                        try:
                            title_input = short_wait.until(EC.presence_of_element_located((By.ID, "edit-field-metatags-0-basic-title")))
                        except:
                            raise Exception("Could not locate meta title field in taxonomy flow")
                    else:
                        for title_selector in ["#edit-field-meta-tags-0-basic-title", "#edit-field-ln-n-meta-tags-0-basic-title"]:
                            try:
                                title_input = short_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, title_selector)))
                                break
                            except:
                                continue
                    if not title_input:
                        raise Exception("Could not locate meta title field")
                    driver.execute_script("arguments[0].value = '';", title_input)
                    driver.execute_script("arguments[0].value = arguments[1];", title_input, meta_title)
                    if click_save_button(driver, wait, website_name, website_lang, is_taxonomy):
                        row_time = time.time() - row_start_time
                        operation_times.append(row_time)
                        success_count[0] += 1
                        processed_rows.add(index)
                        st.success(f"✅ [{index+1}] Updated meta title: {full_url} (Execution time: {format_time(row_time)})")
                    else:
                        raise Exception("Failed to save meta title changes")
                elif task_type == "Meta description":
                    meta_desc = row['Meta Description']
                    if not try_open_metatags_dropdown(wait, driver, website_name):
                        try:
                            # Try direct URL manipulation for taxonomy
                            if is_taxonomy:
                                driver.get(f"{driver.current_url}#edit-field-metatags-0")
                            else:
                                # Try to force open with JavaScript
                                driver.execute_script("""
                                    document.querySelectorAll('summary[aria-controls*=\"meta-tags\"]').forEach(el => {
                                        if (el.getAttribute('aria-expanded') !== 'true') {
                                            el.click();
                                        }
                                    });
                                    document.querySelectorAll('summary[aria-controls*=\"basic\"]').forEach(el => {
                                        if (el.getAttribute('aria-expanded') !== 'true') {
                                            el.click();
                                        }
                                    });
                                """)
                                time.sleep(1)
                            
                            # Verify we can access fields
                            desc_field_present = False
                            for selector in [
                                "#edit-field-metatags-0-basic-description",
                                "#edit-field-ln-n-meta-tags-0-basic-description",
                                "[id*='edit-field-meta-tags'][id*='description']"
                            ]:
                                try:
                                    driver.find_element(By.CSS_SELECTOR, selector)
                                    desc_field_present = True
                                    break
                                except:
                                    continue
                                    
                            if not desc_field_present:
                                raise Exception("Fallback failed to access meta fields")
                                
                        except Exception as fallback_e:
                            raise Exception(f"Both primary and fallback meta tags methods failed: {str(fallback_e)}")

                    short_wait = WebDriverWait(driver, SHORT_WAIT)
                    desc_input = None
                    if is_taxonomy:
                        try:
                            desc_input = short_wait.until(EC.presence_of_element_located((By.ID, "edit-field-metatags-0-basic-description")))
                        except:
                            raise Exception("Could not locate meta description field in taxonomy flow")
                    else:
                        for desc_selector in ["#edit-field-meta-tags-0-basic-description", "#edit-field-ln-n-meta-tags-0-basic-description"]:
                            try:
                                desc_input = short_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, desc_selector)))
                                break
                            except:
                                continue
                    if not desc_input:
                        raise Exception("Could not locate meta description field")
                    driver.execute_script("arguments[0].value = '';", desc_input)
                    driver.execute_script("arguments[0].value = arguments[1];", desc_input, meta_desc)
                    if click_save_button(driver, wait, website_name, website_lang, is_taxonomy):
                        row_time = time.time() - row_start_time
                        operation_times.append(row_time)
                        success_count[0] += 1
                        processed_rows.add(index)
                        st.success(f"✅ [{index+1}] Updated meta description: {full_url} (Execution time: {format_time(row_time)})")
                    else:
                        raise Exception("Failed to save meta description changes")
                elif task_type == "Meta title + description":
                    meta_title = row['Meta Title']
                    meta_desc = row['Meta Description']
                    if not try_open_metatags_dropdown(wait, driver, website_name):
                        try:
                            # Try direct URL manipulation for taxonomy
                            if is_taxonomy:
                                driver.get(f"{driver.current_url}#edit-field-metatags-0")
                            else:
                                # Try to force open with JavaScript
                                driver.execute_script("""
                                    document.querySelectorAll('summary[aria-controls*=\"meta-tags\"]').forEach(el => {
                                        if (el.getAttribute('aria-expanded') !== 'true') {
                                            el.click();
                                        }
                                    });
                                    document.querySelectorAll('summary[aria-controls*=\"basic\"]').forEach(el => {
                                        if (el.getAttribute('aria-expanded') !== 'true') {
                                            el.click();
                                        }
                                    });
                                """)
                                time.sleep(1)
                            
                            # Verify we can access fields
                            fields_present = False
                            for title_selector, desc_selector in zip(
                                ["#edit-field-metatags-0-basic-title", "#edit-field-ln-n-meta-tags-0-basic-title"],
                                ["#edit-field-metatags-0-basic-description", "#edit-field-ln-n-meta-tags-0-basic-description"]
                            ):
                                try:
                                    driver.find_element(By.CSS_SELECTOR, title_selector)
                                    driver.find_element(By.CSS_SELECTOR, desc_selector)
                                    fields_present = True
                                    break
                                except:
                                    continue
                                    
                            if not fields_present:
                                raise Exception("Fallback failed to access meta fields")
                                
                        except Exception as fallback_e:
                            raise Exception(f"Both primary and fallback meta tags methods failed: {str(fallback_e)}")

                    short_wait = WebDriverWait(driver, SHORT_WAIT)
                    title_input = None
                    desc_input = None
                    if is_taxonomy:
                        try:
                            title_input = short_wait.until(EC.presence_of_element_located((By.ID, "edit-field-metatags-0-basic-title")))
                            desc_input = short_wait.until(EC.presence_of_element_located((By.ID, "edit-field-metatags-0-basic-description")))
                        except:
                            raise Exception("Could not locate meta title or description field in taxonomy flow")
                    else:
                        for title_selector, desc_selector in zip(
                            ["#edit-field-meta-tags-0-basic-title", "#edit-field-ln-n-meta-tags-0-basic-title"],
                            ["#edit-field-meta-tags-0-basic-description", "#edit-field-ln-n-meta-tags-0-basic-description"]
                        ):
                            try:
                                title_input = short_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, title_selector)))
                                desc_input = short_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, desc_selector)))
                                break
                            except:
                                continue
                    if not title_input or not desc_input:
                        raise Exception("Could not locate meta title or description field")
                    driver.execute_script("arguments[0].value = '';", title_input)
                    driver.execute_script("arguments[0].value = arguments[1];", title_input, meta_title)
                    driver.execute_script("arguments[0].value = '';", desc_input)
                    driver.execute_script("arguments[0].value = arguments[1];", desc_input, meta_desc)
                    if click_save_button(driver, wait, website_name, website_lang, is_taxonomy):
                        row_time = time.time() - row_start_time
                        operation_times.append(row_time)
                        success_count[0] += 1
                        processed_rows.add(index)
                        st.success(f"✅ [{index+1}] Updated meta title + description: {full_url} (Execution time: {format_time(row_time)})")
                    else:
                        raise Exception("Failed to save meta title + description changes")
                elif task_type == "All":
                    new_alias = slugify_alias(row['New URL Structure'])
                    meta_title = row['Meta Title']
                    meta_desc = row['Meta Description']
                    try:
                        if is_taxonomy:
                            alias_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-field-metatags-0-advanced-canonical-url')))
                        else:
                            alias_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-path-0-alias')))
                        driver.execute_script("arguments[0].value = '';", alias_input)
                        driver.execute_script("arguments[0].value = arguments[1];", alias_input, f'/{new_alias}')
                    except Exception as e:
                        raise Exception(f"Failed to update URL alias: {str(e)}")
                    if not try_open_metatags_dropdown(wait, driver, website_name):
                        try:
                            # Try direct URL manipulation for taxonomy
                            if is_taxonomy:
                                driver.get(f"{driver.current_url}#edit-field-metatags-0")
                            else:
                                # Try to force open with JavaScript
                                driver.execute_script("""
                                    document.querySelectorAll('summary[aria-controls*=\"meta-tags\"]').forEach(el => {
                                        if (el.getAttribute('aria-expanded') !== 'true') {
                                            el.click();
                                        }
                                    });
                                    document.querySelectorAll('summary[aria-controls*=\"basic\"]').forEach(el => {
                                        if (el.getAttribute('aria-expanded') !== 'true') {
                                            el.click();
                                        }
                                    });
                                """)
                                time.sleep(1)
                            
                            # Verify we can access fields
                            fields_present = False
                            for title_selector, desc_selector in zip(
                                ["#edit-field-metatags-0-basic-title", "#edit-field-ln-n-meta-tags-0-basic-title"],
                                ["#edit-field-metatags-0-basic-description", "#edit-field-ln-n-meta-tags-0-basic-description"]
                            ):
                                try:
                                    driver.find_element(By.CSS_SELECTOR, title_selector)
                                    driver.find_element(By.CSS_SELECTOR, desc_selector)
                                    fields_present = True
                                    break
                                except:
                                    continue
                                    
                            if not fields_present:
                                raise Exception("Fallback failed to access meta fields")
                                
                        except Exception as fallback_e:
                            raise Exception(f"Both primary and fallback meta tags methods failed: {str(fallback_e)}")

                    short_wait = WebDriverWait(driver, SHORT_WAIT)
                    title_input = None
                    desc_input = None
                    if is_taxonomy:
                        try:
                            title_input = short_wait.until(EC.presence_of_element_located((By.ID, "edit-field-metatags-0-basic-title")))
                            desc_input = short_wait.until(EC.presence_of_element_located((By.ID, "edit-field-metatags-0-basic-description")))
                        except:
                            raise Exception("Could not locate meta title or description field in taxonomy flow")
                    else:
                        for title_selector, desc_selector in zip(
                            ["#edit-field-meta-tags-0-basic-title", "#edit-field-ln-n-meta-tags-0-basic-title"],
                            ["#edit-field-meta-tags-0-basic-description", "#edit-field-ln-n-meta-tags-0-basic-description"]
                        ):
                            try:
                                title_input = short_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, title_selector)))
                                desc_input = short_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, desc_selector)))
                                break
                            except:
                                continue
                    if not title_input or not desc_input:
                        raise Exception("Could not locate meta title or description field")
                    driver.execute_script("arguments[0].value = '';", title_input)
                    driver.execute_script("arguments[0].value = arguments[1];", title_input, meta_title)
                    driver.execute_script("arguments[0].value = '';", desc_input)
                    driver.execute_script("arguments[0].value = arguments[1];", desc_input, meta_desc)
                    if click_save_button(driver, wait, website_name, website_lang, is_taxonomy):
                        row_time = time.time() - row_start_time
                        operation_times.append(row_time)
                        success_count[0] += 1
                        processed_rows.add(index)
                        st.success(f"✅ [{index+1}] Updated alias + meta title + description: {full_url} → {base_url}/{website_lang[:2].lower()}/{new_alias} (Execution time: {format_time(row_time)})")
                    else:
                        raise Exception("Failed to save alias + meta title + description changes")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                current_progress[0] = min(current_progress[0] + progress_increment * 0.6, 100)
                progress_bar.progress(int(current_progress[0]))
                progress_text.text(f"Progress: {int(current_progress[0])}%{' (Epoch {}/{})'.format(epoch_idx + 1, total_epochs) if use_epochs else ''}")
                status_text.text(f"Completed {index+1}/{total_rows} (Execution time: {format_time(row_time)})")
        except Exception as e:
            row_time = time.time() - row_start_time
            st.error(f"❌ [{index+1}] Error with {row.get('URL', '')}: {str(e)} (Execution time: {format_time(row_time)})")
            failures.append(row.to_dict())
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            current_progress[0] = min(current_progress[0] + progress_increment, 100)
            progress_bar.progress(int(current_progress[0]))
            progress_text.text(f"Progress: {int(current_progress[0])}%{' (Epoch {}/{})'.format(epoch_idx + 1, total_epochs) if use_epochs else ''}")

def run_automation(
    df,
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
):
    base_url = get_base_url(website_name)
    st.success(f"✅ Starting automation for: {base_url} ({website_lang}, {task_type})")
    all_failures = []
    total_start_time = time.time()
    all_operation_times = []
    total_success_count = [0]  # Use list to allow modification in nested function
    total_count = 0
    processed_rows = set()  # Track processed rows

    websitename = get_website_name(website_name)
    use_epochs = websitename == "Nestlé Professional" or show_nestle_mena

    try:
        if task_type == "Upload images with alt text":
            image_paths = save_uploaded_images(images_uploaded)
            st.info(f"Saved {len(image_paths)} images to downloads folder")
            total_images = len(image_paths)
            total_count = total_images
            progress_increment = 100 / total_images if total_images > 0 else 0
            current_progress = [0]  # Use list to allow modification
            alt_texts = {}
            if 'Image Name' in df.columns and 'Alt Text' in df.columns:
                alt_texts = dict(zip(df['Image Name'], df['Alt Text']))
            else:
                st.warning("No alt text data found in the dataframe. Using image names as alt text.")
                alt_texts = {os.path.basename(path): os.path.basename(path).split('.')[0] for path in image_paths}

            driver = initialize_driver()
            wait = WebDriverWait(driver, LONG_WAIT)
            try:
                perform_login(driver, wait, website_name, website_lang, username, password, otp_code, show_shield, shield_username, shield_password, show_nestle_mena, show_nestle_family, otp)
                for i, image_path in enumerate(image_paths):
                    image_start_time = time.time()
                    st.info(f"Processing image {i+1}/{total_images}: {os.path.basename(image_path)}")
                    try:
                        upload_url = f"{base_url}/{'media/add/image' if show_no_lang else 'en/media/add/image'}"
                        driver.execute_script("window.open('');")
                        driver.switch_to.window(driver.window_handles[1])
                        driver.get(upload_url)
                        file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file' and @accept='image/*']")))
                        file_input.send_keys(image_path)
                        status_text.text(f"Uploading {os.path.basename(image_path)}... ({i+1}/{total_images})")
                        current_progress[0] = min(current_progress[0] + progress_increment * 0.3, 100)
                        progress_bar.progress(int(current_progress[0]))
                        progress_text.text(f"Progress: {int(current_progress[0])}%")
                        image_name = os.path.basename(image_path).split('.')[0]
                        name_field = wait.until(EC.presence_of_element_located((By.ID, 'edit-name-0-value')))
                        name_field.clear()
                        name_field.send_keys(image_name)
                        alt_text = alt_texts.get(os.path.basename(image_path), image_name)
                        alt_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id, 'edit-field-media-image-0-alt')]")))
                        alt_field.clear()
                        alt_field.send_keys(alt_text)
                        current_progress[0] = min(current_progress[0] + progress_increment * 0.3, 100)
                        progress_bar.progress(int(current_progress[0]))
                        progress_text.text(f"Progress: {int(current_progress[0])}%")
                        if click_save_button(driver, wait, website_name, website_lang, False):
                            image_time = time.time() - image_start_time
                            all_operation_times.append(image_time)
                            total_success_count[0] += 1
                            processed_rows.add(i)
                            st.success(f"✅ Successfully uploaded and added alt text for {os.path.basename(image_path)} (Execution time: {format_time(image_time)})")
                        else:
                            raise Exception("Failed to save image upload")
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        current_progress[0] = min(current_progress[0] + progress_increment * 0.4, 100)
                        progress_bar.progress(int(current_progress[0]))
                        progress_text.text(f"Progress: {int(current_progress[0])}%")
                        status_text.text(f"Completed {i+1}/{total_images} (Execution time: {format_time(image_time)})")
                    except Exception as e:
                        image_time = time.time() - image_start_time
                        st.error(f"❌ Error processing {os.path.basename(image_path)}: {str(e)} (Execution time: {format_time(image_time)})")
                        all_failures.append({'Image Path': os.path.basename(image_path)})
                        if len(driver.window_handles) > 1:
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                        current_progress[0] = min(current_progress[0] + progress_increment, 100)
                        progress_bar.progress(int(current_progress[0]))
                        progress_text.text(f"Progress: {int(current_progress[0])}%")
                        continue
            except Exception as e:
                st.error(f"❌ Critical error occurred: {str(e)}")
            finally:
                try:
                    driver.quit()
                except:
                    pass
            progress_text.text("Progress: 100%")
            progress_bar.progress(100)

        else:
            total_rows = len(df)
            total_count = total_rows
            if use_epochs:
                epochs = [df[i:i+EPOCH_SIZE] for i in range(0, total_rows, EPOCH_SIZE)]
                total_epochs = len(epochs)
                epoch_progress_increment = 100 / total_epochs if total_epochs > 0 else 0
                current_progress = [0]  # Use list to allow modification

                for epoch_idx, epoch_df in enumerate(epochs):
                    st.info(f"Starting Epoch {epoch_idx + 1}/{total_epochs} with {len(epoch_df)} rows")
                    progress_text.text(f"Progress: {int(current_progress[0])}% (Epoch {epoch_idx + 1}/{total_epochs})")
                    driver = initialize_driver()
                    wait = WebDriverWait(driver, LONG_WAIT)
                    try:
                        perform_login(driver, wait, website_name, website_lang, username, password, otp_code, show_shield, shield_username, shield_password, show_nestle_mena, show_nestle_family, otp)
                        epoch_rows = len(epoch_df)
                        progress_increment = epoch_progress_increment / epoch_rows if epoch_rows > 0 else 0
                        process_rows(driver, wait, epoch_df, base_url, website_name, website_lang, task_type, show_no_lang, total_rows, progress_bar, status_text, progress_text, progress_increment, current_progress, all_operation_times, total_success_count, all_failures, processed_rows, epoch_idx, total_epochs, use_epochs)
                    except Exception as e:
                        st.error(f"❌ Epoch {epoch_idx + 1} failed: {str(e)}")
                    finally:
                        try:
                            driver.quit()
                        except:
                            pass
                    st.info(f"Completed Epoch {epoch_idx + 1}/{total_epochs}")
                    current_progress[0] = min(current_progress[0] + epoch_progress_increment, 100)
                    progress_bar.progress(int(current_progress[0]))
                    progress_text.text(f"Progress: {int(current_progress[0])}% (Epoch {epoch_idx + 1}/{total_epochs})")
                progress_text.text("Progress: 100%")
                progress_bar.progress(100)
            else:
                driver = initialize_driver()
                wait = WebDriverWait(driver, LONG_WAIT)
                try:
                    perform_login(driver, wait, website_name, website_lang, username, password, otp_code, show_shield, shield_username, shield_password, show_nestle_mena, show_nestle_family, otp)
                    progress_increment = 100 / total_rows if total_rows > 0 else 0
                    current_progress = [0]  # Use list to allow modification
                    process_rows(driver, wait, df, base_url, website_name, website_lang, task_type, show_no_lang, total_rows, progress_bar, status_text, progress_text, progress_increment, current_progress, all_operation_times, total_success_count, all_failures, processed_rows, 0, 0, use_epochs)
                except Exception as e:
                    st.error(f"❌ Critical error occurred: {str(e)}")
                finally:
                    try:
                        driver.quit()
                    except:
                        pass
                progress_text.text("Progress: 100%")
                progress_bar.progress(100)

        # Calculate summary statistics
        total_time = time.time() - total_start_time
        avg_time = sum(all_operation_times) / len(all_operation_times) if all_operation_times else 0
        success_percentage = int(total_success_count[0] / total_count * 100) if total_count > 0 else 0
        failure_percentage = int(len(all_failures) / total_count * 100) if total_count > 0 else 0
        incomplete_count = max(0, total_count - (total_success_count[0] + len(all_failures)))  # Prevent negative values
        incomplete_percentage = int(incomplete_count / total_count * 100) if total_count > 0 else 0

        # Build the summary message (always include incomplete count)
        summary_message = (
            f"**📦 End of automation process!** Stopping the application.<br>"
            f"**Total execution time: {format_time(total_time)}**<br>"
            f"**Average time per operation: {format_time(avg_time)}**<br>"
            f"**Total: {total_count}**<br>"
            f"**Success: {total_success_count[0]} ({success_percentage}%)**<br>"
            f"**Failed: {len(all_failures)} ({failure_percentage}%)**<br>"
            f"**Incomplete: {incomplete_count} ({incomplete_percentage}%)**"
        )

        # Display the summary
        st.markdown(summary_message, unsafe_allow_html=True)

        # Handle failure and incomplete reports
        incomplete_rows = []
        if task_type == "Upload images with alt text":
            for i, image_path in enumerate(image_paths):
                if i not in processed_rows:
                    incomplete_rows.append({'Image Path': os.path.basename(image_path)})
        else:
            for index, row in df.iterrows():
                if index not in processed_rows:
                    incomplete_rows.append(row.to_dict())

        # Generate failure report only if there are failures or incomplete items
        if len(all_failures) > 0 or len(incomplete_rows) > 0:
            # Combine failures and incomplete items into one DataFrame
            fail_df = pd.DataFrame(all_failures)
            incomplete_df = pd.DataFrame(incomplete_rows)
            
            # Remove unwanted columns if they exist
            for df in [fail_df, incomplete_df]:
                if 'error' in df.columns:
                    df.drop('error', axis=1, inplace=True)
                if 'screenshot' in df.columns:
                    df.drop('screenshot', axis=1, inplace=True)
                if 'Status' in df.columns:
                    df.drop('Status', axis=1, inplace=True)
            
            # Combine both DataFrames and drop duplicates based on URL
            combined_df = pd.concat([fail_df, incomplete_df], ignore_index=True)
            
            # Drop duplicates - assuming 'URL' is the column that identifies unique rows
            if 'URL' in combined_df.columns:
                combined_df = combined_df.drop_duplicates(subset=['URL'], keep='first')
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                combined_df.to_excel(writer, index=False, sheet_name='Failures Report')
            
            output.seek(0)
            st.success("Failure report generated successfully!")
            st.download_button(
                label="Download Failures Report",
                data=output,
                file_name=f"{get_website_name(website_name)}_{website_lang}_Failures_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No failures or incomplete items. No report generated.")

        # Stop the Streamlit app after completion
        st.stop()

    except Exception as e:
        st.error(f"❌ Critical error occurred: {str(e)}")
        progress_bar.progress(100)
        progress_text.text("Progress: 100%")
        # Calculate summary statistics
        total_time = time.time() - total_start_time
        avg_time = sum(all_operation_times) / len(all_operation_times) if all_operation_times else 0
        success_percentage = int(total_success_count[0] / total_count * 100) if total_count > 0 else 0
        failure_percentage = int(len(all_failures) / total_count * 100) if total_count > 0 else 0
        incomplete_count = max(0, total_count - (total_success_count[0] + len(all_failures)))  # Prevent negative values
        incomplete_percentage = int(incomplete_count / total_count * 100) if total_count > 0 else 0

        # Build the summary message (always include incomplete count)
        summary_message = (
            f"**📦 End of automation process!** Stopping the application.<br>"
            f"**Total execution time: {format_time(total_time)}**<br>"
            f"**Average time per operation: {format_time(avg_time)}**<br>"
            f"**Total: {total_count}**<br>"
            f"**Success: {total_success_count[0]} ({success_percentage}%)**<br>"
            f"**Failed: {len(all_failures)} ({failure_percentage}%)**<br>"
            f"**Incomplete: {incomplete_count} ({incomplete_percentage}%)**"
        )

        # Display the summary
        st.markdown(summary_message, unsafe_allow_html=True)

        # Handle failure and incomplete reports
        incomplete_rows = []
        if task_type == "Upload images with alt text":
            for i, image_path in enumerate(image_paths):
                if i not in processed_rows:
                    incomplete_rows.append({'Image Path': os.path.basename(image_path)})
        else:
            for index, row in df.iterrows():
                if index not in processed_rows:
                    incomplete_rows.append(row.to_dict())

        # Generate failure report only if there are failures or incomplete items
        if len(all_failures) > 0 or len(incomplete_rows) > 0:
        # Combine failures and incomplete items into one DataFrame
            fail_df = pd.DataFrame(all_failures)
            incomplete_df = pd.DataFrame(incomplete_rows)
            
            # Remove unwanted columns if they exist
            for df in [fail_df, incomplete_df]:
                if 'error' in df.columns:
                    df.drop('error', axis=1, inplace=True)
                if 'screenshot' in df.columns:
                    df.drop('screenshot', axis=1, inplace=True)
                if 'Status' in df.columns:
                    df.drop('Status', axis=1, inplace=True)
            
            # Combine both DataFrames and drop duplicates based on URL
            combined_df = pd.concat([fail_df, incomplete_df], ignore_index=True)
            
            # Drop duplicates - assuming 'URL' is the column that identifies unique rows
            if 'URL' in combined_df.columns:
                combined_df = combined_df.drop_duplicates(subset=['URL'], keep='first')
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                combined_df.to_excel(writer, index=False, sheet_name='Failures Report')
            
            output.seek(0)
            st.success("Failure report generated successfully!")
            st.download_button(
                label="Download Failures Report",
                data=output,
                file_name=f"{get_website_name(website_name)}_{website_lang}_Failures_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No failures or incomplete items. No report generated.")

        # Stop the Streamlit app after error handling
        st.stop()