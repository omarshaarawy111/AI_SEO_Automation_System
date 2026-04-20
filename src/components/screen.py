import time 
import streamlit as st 
import logging 
import platform 
import pyautogui
import threading

# Global variable to control the screen-awake thread (module-level)
keep_awake_running = False
keep_awake_thread = None

# Set up logging 
logger = logging.getLogger(__name__) 

def system_inti():
    # Configure pyautogui 
    pyautogui.FAILSAFE = True  # Move mouse to upper-left corner to abort 
    pyautogui.PAUSE = 0.1  # Small pause for each pyautogui action 

def log_to_streamlit(message, level="info"):
    """Helper function to safely log messages to Streamlit from any thread."""
    try:
        if st.runtime.exists():
            with st.empty():
                if level == "info":
                    st.info(message)
                elif level == "warning":
                    st.warning(message)
                elif level == "error":
                    st.error(message)
    except:
        pass  # If we can't log to Streamlit, continue silently
    
    # Always log to console as well
    if level == "info":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)

def start_keep_awake():
    """Start the keep-awake thread"""
    global keep_awake_running, keep_awake_thread
    
    if keep_awake_thread and keep_awake_thread.is_alive():
        log_to_streamlit("Keep-awake thread is already running")
        return
    
    keep_awake_running = True
    keep_awake_thread = threading.Thread(target=keep_system_awake, daemon=True)
    keep_awake_thread.start()
    log_to_streamlit("Keep-awake thread started")

def stop_keep_awake():
    """Stop the keep-awake thread"""
    global keep_awake_running
    
    keep_awake_running = False
    log_to_streamlit("Keep-awake thread stopping...")

def keep_system_awake(): 
    """Run in a background thread to prevent system sleep by simulating user activity.""" 
    global keep_awake_running 
    log_to_streamlit("Keep-awake thread started to prevent system sleep.") 
    last_activity_time = time.time() 
    
    # More frequent checks (every 30 seconds instead of 240) 
    CHECK_INTERVAL = 30 
    # Activity interval (3 minutes instead of 4 minutes) 
    ACTIVITY_INTERVAL = 180 
    
    while keep_awake_running: 
        current_time = time.time() 
        # Check if it's time to simulate activity 
        if current_time - last_activity_time >= ACTIVITY_INTERVAL: 
            try: 
                log_to_streamlit("Simulating user activity to prevent system sleep") 
                
                # Get current mouse position 
                original_pos = pyautogui.position() 
                
                # Method 1: Mouse movement (more noticeable - 5 pixels instead of 1) 
                pyautogui.moveRel(5, 0, duration=0.1)  # Move 5 pixels right 
                time.sleep(0.1) 
                pyautogui.moveRel(-5, 0, duration=0.1)  # Move back 
                time.sleep(0.1) 
                
                # Method 2: Keyboard activity (Shift key press) 
                pyautogui.keyDown('shift') 
                time.sleep(0.05) 
                pyautogui.keyUp('shift') 
                time.sleep(0.05) 
                
                # Method 3: Additional mouse movement 
                pyautogui.moveRel(0, 3, duration=0.1)  # Move 3 pixels down 
                time.sleep(0.1) 
                pyautogui.moveRel(0, -3, duration=0.1)  # Move back 
                time.sleep(0.1) 
                
                # Return to original position 
                pyautogui.moveTo(original_pos.x, original_pos.y, duration=0.1) 
                
                log_to_streamlit("Activity simulation completed") 
                last_activity_time = current_time 
                
            except pyautogui.FailSafeException: 
                log_to_streamlit("PyAutoGUI failsafe triggered - mouse moved to upper-left corner", "warning") 
                break 
            except Exception as e: 
                log_to_streamlit(f"Error during activity simulation: {str(e)}", "error") 
                # Continue with next iteration despite errors 
                
        # Shorter sleep for more responsive checking 
        time.sleep(CHECK_INTERVAL) 
        
    log_to_streamlit("Keep-awake thread stopped")