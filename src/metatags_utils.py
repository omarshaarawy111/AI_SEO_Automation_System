from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from config import get_website_name
import streamlit as st
import time
from sidebar_utils import open_sidebar_with_all_methods

# Constants for sleep timings
SHORT_WAIT = 4 # For meta tags and basic tags
LONG_WAIT = 6  # For page loads and edit buttons
SAVE_TIMEOUT = 5  # For save operations
MOM_AND_ME_WAIT = 6 # For Mom and Me dialog wait time

def try_open_metatags_dropdown(wait, driver, website_name):
    """
    Enhanced method to open meta tags dropdown handling all cases:
    - Taxonomy pages
    - Nestlé Professional sidebar
    - Non-Nestlé Professional pages
    - Basic tags expansion
    """

    websitename = get_website_name(website_name)
    
    # Special handling for Mom and Me - use specialized function
   
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
            raise Exception("No valid meta tags link found!")
        except Exception as e:
            st.error(f"Failed to open meta tags section in taxonomy flow!")
            return False
    else:
        # Handle different website types
        if websitename in ["Nestlé Professional"]:
            # Nestlé Professional requires sidebar opening
            if not open_sidebar_with_all_methods(driver, SHORT_WAIT):
                st.error("Failed to open sidebar!")
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
    """Check if an error message is present on the page and return its text."""
    try:
        # Check for error messages in multiple languages
        error_selectors = [
            ".messages--error", 
            ".alert-danger", 
            "div[role='alert']",
            "div[role='contentinfo'][aria-labelledby*='error']",  # Specific to your error message
            "div.error",  # English error
            "div.erreur",  # French error
            "div.خطأ",  # Arabic error
            "div.رسالة-خطأ",  # Arabic error message
            "div[contains(text(), 'error')]",  # English
            "div[contains(text(), 'erreur')]",  # French
            "div[contains(text(), 'خطأ')]",  # Arabic
            "div[contains(text(), 'حفظ')][contains(@class, 'error')]",  # Arabic save error
            "div.messages-list__item.messages.messages--error"  # Specific class for this error
        ]
        
        for selector in error_selectors:
            try:
                # Use a shorter timeout for each selector
                quick_wait = WebDriverWait(driver, 1)
                error_element = quick_wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if error_element and error_element.is_displayed():
                    error_text = error_element.text
                    # Additional check for the specific error content
                    if "1 error has been found" in error_text or "From" in error_text:
                        return error_text
            except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
                continue
        
        # Additional check for the specific error message content
        try:
            error_divs = driver.find_elements(By.CSS_SELECTOR, "div[role='contentinfo']")
            for div in error_divs:
                if div.is_displayed() and ("is already being redirected" in div.text or 
                                         "1 error has been found" in div.text):
                    return div.text
        except:
            pass
            
        return None
        
    except Exception:
        return None

def verify_save_success(driver, wait, original_edit_url):
    """
    Verify save success by checking if '/edit' is no longer in the URL.
    Also checks for specific error messages that indicate save failure.
    Returns True if successfully saved, False otherwise.
    
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
        
        # Wait for URL to change with a reasonable timeout
        wait.until(is_edit_page_gone)
        
        # Check for error messages to be sure
        error_message = check_for_error_message(driver, WebDriverWait(driver, 2))
        if error_message:
            # Check for specific error patterns
            if ("is already being redirected" in error_message or
                "1 error has been found" in error_message or
                "From" in error_message or
                "edit-redirect-source" in error_message):
                return False
            
        return True
        
    except TimeoutException:
        # If we're still on an edit page after timeout
        current_url = driver.current_url.split('?')[0]
        if '/edit' in current_url:
            # Check for the specific redirect error
            error_message = check_for_error_message(driver, WebDriverWait(driver, 2))
            if error_message and ("1 error has been found" in error_message or "From" in error_message):
                st.error("Save failed due to redirect validation error!")
                return False
            return False
            
        # Check for error messages even if URL changed
        error_message = check_for_error_message(driver, WebDriverWait(driver, 2))
        if error_message and ("1 error has been found" in error_message or "From" in error_message):
            st.error("Save failed due to redirect validation error!")
            return False
            
        # If no error messages and no /edit in URL, assume success
        return True

def handle_nestle_mena_confirmation(driver, wait):
    """Handle the confirmation dialog that appears after saving on Nestlé MENA websites."""
    try:
        # Wait for the dialog to appear
        confirmation_dialog = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ui-dialog[aria-describedby*='ui-id']"))
        )
        
        # Wait for the "Yes" button to be clickable
        yes_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ui-dialog-buttonpane button.button--primary"))
        )
        
        # Click the "Yes" button
        driver.execute_script("arguments[0].click();", yes_button)
        
        # Wait for the dialog to disappear
        wait.until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.ui-dialog[aria-describedby*='ui-id']"))
        )
        
        return True
    except Exception as e:
        st.warning(f"Failed to handle Nestlé MENA confirmation dialog: {str(e)}")
        return False

def click_save_button(driver, wait, website_name, website_lang, is_taxonomy):
    """Enhanced save button click with /edit URL validation and Nestlé MENA confirmation handling"""
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
                raise Exception("No save button found for taxonomy!")
        else:
            # Handle all possible save button variations for non-taxonomy
            save_button_selectors = [
                "#gin-sticky-edit-submit",
                "#edit-submit",
                "input[value='Save']",
                "input[value='Save (this translation)']",
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
                raise Exception("No save button found!")
        
        # Scroll to and click the save button
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
        driver.execute_script("arguments[0].click();", save_button)
        
        # Special handling for Nestlé MENA confirmation dialog
        if websitename == "Nestlé Mena":
            if not handle_nestle_mena_confirmation(driver, wait):
                raise Exception("Failed to handle Nestlé MENA confirmation dialog!")
        
        # Verify success by checking if we're no longer on an edit page
        if verify_save_success(driver, wait, original_edit_url):
            return True
            
        # If verify_save_success returned False, check for specific error types
        error_message = check_for_error_message(driver, WebDriverWait(driver, 2))
        if error_message:
            
            st.error(f"Save failed with error: {error_message}")
            return False
        else:
            return False
            
    except Exception as e:
        st.error(f"Failed to click save button: {str(e)}")
        return False

def try_open_metatags_dropdown_mom_and_me(driver, wait):

    # Special handling for Mom and Me - use specialized function
   
    short_wait = WebDriverWait(driver, SHORT_WAIT)
    
    # Check if URL contains "/taxonomy" for taxonomy flow
    is_taxonomy = "/taxonomy" in driver.current_url
    
    if is_taxonomy:
        # Enhanced taxonomy flow handling
        # Step 1
        time.sleep(SHORT_WAIT)
        for selector in [
                "a[href='#edit-field-metatags-0']",
                "a[href*='edit-field-meta-tags']"
            ]:
            try:
                meta_tags_link = short_wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                meta_tags_link.click()
            except:
                continue    
        # Step 2: Locate and click "Edit meta tags" button
        edit_meta_selectors = [
            "a[data-drupal-selector='edit-field-meta-tags-0-link']",  # Primary selector from HTML
            "a#edit-field-meta-tags-0-link",  # Direct ID selector
            "a.button.use-ajax[href*='metatag/entity']",  # AJAX button selector
            "a[href*='metatag'][href*='edit']"  # Fallback selector
        ]
        
        edit_meta_link = None
        for selector in edit_meta_selectors:
            try:
                edit_meta_link = WebDriverWait(driver, LONG_WAIT).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                break
            except Exception:
                continue
        
        if not edit_meta_link:
            st.error("Failed working 'Edit meta tags' button !")
            return False
        
        # Step 3: Click the button and wait for dialog
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_meta_link)
        driver.execute_script("arguments[0].click();", edit_meta_link)
        
        # Step 4: Wait for sidebar to open (3-4 seconds as specified)
        time.sleep(MOM_AND_ME_WAIT)

        
        
        
        # Step 5: Expand Basic tags section if needed
        basic_tags_selectors = [
            "summary.claro-details__summary[aria-controls*='basic']",
            "summary.claro-details__summary",
            "summary[aria-controls*='basic']",
            "summary[aria-controls*='POpFfB7CKDw']"
        ]
        
        basic_tags = None
        for selector in basic_tags_selectors:
            try:
                basic_tags = WebDriverWait(driver, SHORT_WAIT).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                break
            except Exception:
                continue
        
        if basic_tags:
            if basic_tags.get_attribute("aria-expanded") != "true":
                driver.execute_script("arguments[0].click();", basic_tags)
        
        # Step 6: Verify fields are accessible
        title_selectors = [
            "input[data-drupal-selector='edit-metatags-basic-title']",
            "input[name='metatags[basic][title]']"
        ]
        
        desc_selectors = [
            "textarea[data-drupal-selector='edit-metatags-basic-description']",
            "textarea[name='metatags[basic][description]']"
        ]
        
        # Verify title field is present
        title_field = None
        for selector in title_selectors:
            try:
                title_field = WebDriverWait(driver, SHORT_WAIT).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                break
            except Exception:
                continue
        
        # Verify description field is present
        desc_field = None
        for selector in desc_selectors:
            try:
                desc_field = WebDriverWait(driver, SHORT_WAIT).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                break
            except Exception:
                continue
        
        if not title_field or not desc_field:
            st.error("Meta title or description fields not found!")
            return False
        
        return True
    else :
        short_wait = WebDriverWait(driver, SHORT_WAIT)
        # Step 1: Open sidebar and open meta tags drop down
        if not open_sidebar_with_all_methods(driver, SHORT_WAIT):
            st.error("Failed to open sidebar!")
            return False
        
        # Try multiple meta tags selectors
        meta_selectors = [
                "summary[aria-controls='edit-field-meta-tags-0']",
                "summary[aria-controls='edit-field-ln-n-meta-tags-0']",
                "button[aria-controls*='edit-field-meta-tags']",
                "summary.claro-details__summary"
            ]

        # Attempt to expand meta tags section
        for selector in meta_selectors:
            try :
                element = short_wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        
                # Toggle if not expanded
                if element.get_attribute("aria-expanded") != "true":
                    driver.execute_script("arguments[0].click();", element)
    
            except Exception as e:
                continue    
                
        

                
        # Step 2: Locate and click "Edit meta tags" button
        edit_meta_selectors = [
            "a[data-drupal-selector='edit-field-meta-tags-0-link']",  # Primary selector from HTML
            "a#edit-field-meta-tags-0-link",  # Direct ID selector
            "a.button.use-ajax[href*='metatag/entity']",  # AJAX button selector
            "a[href*='metatag'][href*='edit']"  # Fallback selector
        ]
        
        edit_meta_link = None
        for selector in edit_meta_selectors:
            try:
                edit_meta_link = WebDriverWait(driver, LONG_WAIT).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                break
            except Exception:
                continue
        
        if not edit_meta_link:
            st.error("Failed working 'Edit meta tags' button !")
            return False
        
        # Step 3: Click the button and wait for dialog
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_meta_link)
        driver.execute_script("arguments[0].click();", edit_meta_link)
        
        # Step 4: Wait for sidebar to open (3-4 seconds as specified)
        time.sleep(MOM_AND_ME_WAIT)

        
        
        
        # Step 5: Expand Basic tags section if needed
        basic_tags_selectors = [
            "summary.claro-details__summary[aria-controls*='basic']",
            "summary.claro-details__summary",
            "summary[aria-controls*='basic']",
            "summary[aria-controls*='POpFfB7CKDw']"
        ]
        
        basic_tags = None
        for selector in basic_tags_selectors:
            try:
                basic_tags = WebDriverWait(driver, SHORT_WAIT).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                break
            except Exception:
                continue
        
        if basic_tags:
            if basic_tags.get_attribute("aria-expanded") != "true":
                driver.execute_script("arguments[0].click();", basic_tags)
        
        # Step 6: Verify fields are accessible
        title_selectors = [
            "input[data-drupal-selector='edit-metatags-basic-title']",
            "input[name='metatags[basic][title]']"
        ]
        
        desc_selectors = [
            "textarea[data-drupal-selector='edit-metatags-basic-description']",
            "textarea[name='metatags[basic][description]']"
        ]
        
        # Verify title field is present
        title_field = None
        for selector in title_selectors:
            try:
                title_field = WebDriverWait(driver, SHORT_WAIT).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                break
            except Exception:
                continue
        
        # Verify description field is present
        desc_field = None
        for selector in desc_selectors:
            try:
                desc_field = WebDriverWait(driver, SHORT_WAIT).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                break
            except Exception:
                continue
        
        if not title_field or not desc_field:
            st.error("Meta title or description fields not found!")
            return False
        
        return True

def update_meta_title_mom_and_me(driver, wait, meta_title):
    """
    Update meta title for Mom and Me website
    """
    title_selectors = [
        "input[data-drupal-selector='edit-metatags-basic-title']",
        "input[name='metatags[basic][title]']"
    ]
    
    title_input = None
    for selector in title_selectors:
        try:
            title_input = WebDriverWait(driver, SHORT_WAIT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            break
        except Exception:
            continue
    
    if not title_input:
        raise Exception("Failed to locate meta title field!")
    
    title_input.clear()
    title_input.send_keys(meta_title)
    time.sleep(0.5)

def update_meta_description_mom_and_me(driver, wait, meta_desc):
    """
    Update meta description for Mom and Me website
    """
    desc_selectors = [
        "textarea[data-drupal-selector='edit-metatags-basic-description']",
        "textarea[name='metatags[basic][description]']"
    ]
    
    desc_input = None
    for selector in desc_selectors:
        try:
            desc_input = WebDriverWait(driver, SHORT_WAIT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            break
        except Exception:
            continue
    
    if not desc_input:
        raise Exception("Failed to locate meta description field!")
    
    desc_input.clear()
    desc_input.send_keys(meta_desc)
    # Add a small wait to ensure the value is properly set
    time.sleep(0.5)

def click_save_button_mom_and_me(driver, wait):
    """
    Specialized save button click for Mom and Me dialog
    """
    try:
        # Try multiple save button selectors
        save_button_selectors = [
            "input[data-drupal-selector='edit-submit']",
            "input[type='submit'][value='Save']",
            "button[data-drupal-selector='edit-submit']",
            "button[type='submit']",
            "input[id='gin-sticky-edit-submit']"
        ]
        
        save_button = None
        for selector in save_button_selectors:
            try:
                save_button = WebDriverWait(driver, LONG_WAIT).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                break
            except Exception:
                continue
        
        if not save_button:
            raise Exception("Failed to find save button!")
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
        driver.execute_script("arguments[0].click();", save_button)
        
        # Wait a moment for the save action to process
        time.sleep(1)
        
        original_edit_url = driver.current_url  # Capture URL before saving

        # Verify success by checking if we're no longer on an edit page
        if verify_save_success(driver, wait, original_edit_url):
            # Switch back to main content after successful save
            try:
                driver.switch_to.default_content()
            except Exception:
                pass
            return True
            
        # If verify_save_success returned False, check for error messages
        error_message = check_for_error_message(driver, WebDriverWait(driver, 2))
        if error_message:
            return False
        else:
            raise Exception("Failed to Save operation!")
        
    except Exception as e:
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
        st.error(f"Failed to click save button in Mom and Me dialog: {str(e)}")
        return False