from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import streamlit as st
import time
from selenium.webdriver.common.keys import Keys


# Constants for sleep timings
LONG_WAIT = 5  # For page loads and edit buttons

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
      
        try:   
            # Handle cookie consent if present
            try:                
                cookie_selectors = [
                    "#onetrust-accept-btn-handler",
                    ".cookie-accept-btn",
                    ".accept-cookies",
                    "#cookie-accept",
                    "#accept-cookies",
                    "button.cookie-btn",
                    "button[aria-label='Accept cookies']"
                ]
                for i in range(3):
                    for selector in cookie_selectors:
                        try:
                            cookie_btn = WebDriverWait(driver, 2).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                            driver.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", cookie_btn)
                            time.sleep(1)
                            break
                        except:
                            continue
                    break    
                  
            except Exception as e:
                st.error(f"Could not find cookie acceptance button!")

        except:
            for attem in range(3):
                try:
                    cookie_btn = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 
                        "#block-consumer-me-babymenavigationassistantblock > button.btn.btn-primary.icon-only.btn-lg.navigation-assistant-button-close"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", cookie_btn)
                    break
                except:
                    continue        

        # Handle different login forms with improved button selectors
        login_attempts = [
            # Nestlé Family login
            {
                'condition': show_nestle_family,
                'selectors': {
                    'username': "#edit-name--3",
                    'password': "#edit-pass--3",
                    'submit': "#edit-actions--5, #edit-submit, button[type='submit'], input[type='submit']"
                }
            },
            # Standard Drupal login with multiple button selectors
            {
                'condition': True,
                'selectors': {
                    'username': "#edit-name, input[name='name']",
                    'password': "#edit-pass, input[name='pass']",
                    'submit': "#edit-submit, button[data-drupal-selector='edit-submit'], input[value='Log in'], button:contains('Log in'), [name='op'][value='Log in']"
                }
            },
            # Generic login form fallback
            {
                'condition': True,
                'selectors': {
                    'username': "input[name='name'], input[name='username'], #username",
                    'password': "input[name='pass'], input[name='password'], #password",
                    'submit': "input[type='submit'], button[type='submit'], .btn-primary, .login-btn, .submit-btn"
                }
            }
        ]

        for attempt in login_attempts:
            if not attempt['condition']:
                continue
                
            try:
                # Wait for username field
                username_field = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, attempt['selectors']['username'])))
                username_field.clear()
                username_field.send_keys(username)
                
                password_field = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, attempt['selectors']['password'])))
                password_field.clear()
                password_field.send_keys(password)
                
                # Multiple strategies to find and click the submit button
                submit_button = None
                submit_selectors = attempt['selectors']['submit'].split(', ')
                
                for selector in submit_selectors:
                    try:
                        submit_button = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector.strip())))
                        break
                    except:
                        continue
                
                if submit_button:
                    # Try multiple click methods
                    try:
                        submit_button.click()
                    except:
                        try:
                            driver.execute_script("arguments[0].click();", submit_button)
                        except:
                            driver.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", submit_button)
                    
                    time.sleep(2)  # Wait for potential page change
                
                # Alternative: Try pressing Enter on password field
                try:
                    password_field.send_keys(Keys.RETURN)
                    time.sleep(2)
                except:
                    pass
                
                # Check for OTP requirement
                if otp:
                    try:
                        # Wait for OTP field
                        otp_field = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "#edit-code, input[name='code'], #otp, #mfaCode")))
                        otp_field.clear()
                        otp_field.send_keys(otp_code)
                        
                        # Find and click verify button
                        verify_button_selectors = [
                            "#edit-login",
                            "button[type='submit']",
                            "#verify",
                            "#submit",
                            ".verify-btn"
                        ]
                        
                        for selector in verify_button_selectors:
                            try:
                                verify_button = WebDriverWait(driver, 2).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                                driver.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", verify_button)
                                time.sleep(4)
                                break
                            except:
                                continue
                        
                    except Exception as e:
                        st.error("OTP verification failed!")
                        st.error(f"❌ Automation has been stopped due to fetal error!")
                        st.stop()

                # Verify login success
                try:
                    if not show_nestle_family:
                        # Multiple ways to verify successful login
                        verification_selectors = [
                            "body.logged-in",
                            ".toolbar-tray",
                            ".user-logged-in",
                            ".user-info",
                            "#user-menu",
                            ".account-menu"
                        ]
                        
                        for selector in verification_selectors:
                            try:
                                WebDriverWait(driver, 3).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                                st.success("Login successful!")
                                return True
                            except:
                                continue
                        
                        # Also check URL changes or title changes
                        current_url = driver.current_url
                        if "user" in current_url or "account" in current_url or "dashboard" in current_url:
                            st.success("Login successful!")
                            return True
                            
                    else:
                        time.sleep(LONG_WAIT)
                        WebDriverWait(driver, 5).until(
                            EC.title_contains("Profile") 
                        )
                        st.success("Login successful!")
                        return True
                        
                except Exception as e:
                    st.error("Login verification failed!")
                    continue
                    
            except Exception as e:
                st.error(f"Login attempt failed!")
                continue
        
        # If all attempts failed, try a final generic approach
        try:
            # Find any submit button and click it
            all_buttons = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
            for button in all_buttons:
                if button.is_displayed() and ("log in" in button.text.lower() or "sign in" in button.text.lower() or button.get_attribute("value") == "Log in"):
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(3)
                    break
        except:
            pass
            
        return False

    except Exception as e:
        st.error(f"Login process failed!")
        st.error(f"❌ Automation has been stopped due to fetal error!")
        st.stop()