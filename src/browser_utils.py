from selenium import webdriver
import streamlit as st
import platform

# Import pywin32 for Windows-specific window minimization
try:
    import win32gui
    import win32con
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False
    st.warning("pywin32 not installed. Using Selenium's minimize_window() as fallback for browser minimization.")

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
    
    driver = webdriver.Chrome(options=options)
    
    # Minimize the browser window
    if platform.system() == "Windows" and PYWIN32_AVAILABLE:
        hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    else:
        driver.minimize_window()
    
    return driver