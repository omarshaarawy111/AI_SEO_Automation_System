from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import streamlit as st
import time

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