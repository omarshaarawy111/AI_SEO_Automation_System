from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from file_utils import get_base_url, slugify_url, slugify_alias
from image_utils import save_uploaded_images
from config import get_website_name
from browser_utils import initialize_driver, format_time
from metatags_utils import try_open_metatags_dropdown, click_save_button, try_open_metatags_dropdown_mom_and_me, update_meta_title_mom_and_me, update_meta_description_mom_and_me, click_save_button_mom_and_me
from login_utils import perform_login
import streamlit as st
import time
import os
import pandas as pd
import io
import datetime
from pathlib import Path

# Constants for sleep timings
SHORT_WAIT = 2
LONG_WAIT = 3
EPOCH_SIZE = 20

# Store all log messages during automation
automation_logs = []

def log_message(message):
    """Store log messages for later saving"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    automation_logs.append(log_entry)
    print(log_entry)  # Also print to console

def calculate_human_time(task_type, operation_count):
    """Calculate estimated human time based on task type and operation count"""
    # Define average human time per operation in seconds for each task type
    human_times = {
        "Add H1": 60,  # 1 minute
        "Meta title": 60,  # 1 minute
        "Meta description": 60,  # 1 minute
        "URL update": 60,  # 1 minute
        "URL redirection": 60,  # 1 minute
        "Meta title + description": 90,  # 1.5 minutes
        "Add H1 + meta title + description": 120,  # 2 minutes
        "All": 180,  # 3 minutes
        "Upload images with alt text": 120  # 2 minutes per image
    }
    
    avg_human_time_per_op = human_times.get(task_type, 60)  # Default to 1 minute
    total_human_time = avg_human_time_per_op * operation_count
    return total_human_time, avg_human_time_per_op

def save_automation_log(website_name, website_lang, summary_message, logs):
    """Save automation logs to file in Downloads/Automation logs folder"""
    try:
        # Create Automation logs directory structure
        downloads_path = Path.home() / "Downloads"
        automation_logs_dir = downloads_path / "Automation logs"
        automation_logs_dir.mkdir(exist_ok=True)
        
        # Create year folder
        current_year = datetime.datetime.now().year
        year_dir = automation_logs_dir / str(current_year)
        year_dir.mkdir(exist_ok=True)
        
        # Create month folder
        current_month = datetime.datetime.now().strftime("%B")
        month_dir = year_dir / current_month
        month_dir.mkdir(exist_ok=True)
        
        # Create log file name - Use get_website_name to get the proper website name
        website_display_name = get_website_name(website_name)
        current_day = datetime.datetime.now().day
        # Remove any special characters that might cause file naming issues
        clean_website_name = website_display_name.replace(" ", "_").replace("/", "_")
        clean_lang = website_lang.replace(" ", "_")
        # Get current datetime - FIXED LINE
        now = datetime.datetime.now()  # Use datetime.datetime.now()
        timestamp = now.strftime("%H-%M-%S")
        log_filename = f"{clean_website_name}_{clean_lang}_Log_Report_{current_month}_{current_day}_{current_year}_time_{timestamp}.txt"
        log_file_path = month_dir / log_filename
        
        # Write log file
        with open(log_file_path, 'w', encoding='utf-8') as f:
            f.write("AUTOMATION LOG REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write("SUMMARY:\n")
            f.write("-" * 20 + "\n")
            # Remove HTML tags from summary message for text file
            summary_clean = summary_message.replace("<br>", "\n").replace("**", "")
            f.write(summary_clean + "\n\n")
            
        
        log_message(f"Log file saved: {log_file_path}")
        return log_file_path
    except Exception as e:
        log_message(f"Error saving log file: {str(e)}")
        return None

def process_rows(driver, wait, epoch_df, base_url, website_name, website_lang, task_type, show_no_lang, total_rows, progress_bar, status_text, progress_text, progress_increment, current_progress, operation_times, success_count, failures, processed_rows, epoch_idx, total_epochs, use_epochs):

    if task_type == "Fix Redirects Status Code":
        total_processed = 0
        total_fixed = 0
        local_operation_times = []  # This will track ALL operation times (success + failure)
        local_failures = []  # Local failures list for this task
        
        try:
            # Navigate to redirect management page with filter for 302 redirects (status_code=3)
            redirect_url = f"{base_url}/admin/config/search/redirect?language=All&order=created&redirect_redirect__uri=&redirect_source__path=&sort=desc&status_code=3&page=2"
            
            log_message(f"Starting redirect fix task on: {redirect_url}")
            progress_bar.progress(5)
            progress_text.text(f"Progress: 5%")
            
            try:
                driver.get(redirect_url)
                # Wait for page to load with longer timeout
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.redirect-list, .views-table, table")))
                time.sleep(3)  # Give more time for page to stabilize
            except Exception as e:
                log_message(f"Error loading redirect page: {str(e)}")
                # Try alternative URL pattern
                try:
                    redirect_url = f"{base_url}/admin/config/search/redirect"
                    driver.get(redirect_url)
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table, .views-table, .redirect-list")))
                    time.sleep(3)
                    log_message(f"Loaded redirect page via alternative URL")
                except Exception as alt_e:
                    error_msg = f"❌ Failed to load redirect management page: {str(alt_e)}"
                    st.error(error_msg)
                    log_message(error_msg)
                    return
            
            # Helper function to check if we're on the last page
            def is_last_page():
                """Check if current page is the last one"""
                try:
                    # Check for disabled next button
                    disabled_selectors = [
                        "li.pager__item--next.pager__item--disabled",
                        "li.pager-next.pager-disabled",
                        "li.next.disabled",
                        "a.pager-next.disabled",
                        "li[class*='pager'][class*='disabled']"
                    ]
                    
                    for selector in disabled_selectors:
                        try:
                            disabled_element = driver.find_element(By.CSS_SELECTOR, selector)
                            if disabled_element:
                                log_message(f"Found disabled next button: {selector}")
                                return True
                        except:
                            continue
                    
                    # Check if next button doesn't exist
                    next_button_selectors = [
                        "li.pager__item--next a",
                        "a.pager-next",
                        "a[title='Go to next page']",
                        "li.next a",
                        "//a[contains(text(), 'next') or contains(text(), 'Next')]",
                        "//li[contains(@class, 'pager-next')]//a"
                    ]
                    
                    for selector in next_button_selectors:
                        try:
                            next_btn = driver.find_element(By.CSS_SELECTOR, selector) if not selector.startswith("//") else driver.find_element(By.XPATH, selector)
                            if next_btn and next_btn.is_displayed():
                                return False  # Has next page
                        except:
                            continue
                    
                    # If no next button found at all, might be single page
                    log_message("No next page button found, assuming last page")
                    return True
                    
                except Exception as e:
                    log_message(f"Error checking last page: {str(e)}")
                    return True  # Assume last page on error
            
            def navigate_to_next_page():
                """Navigate to the next page and return True if successful"""
                try:
                    next_button_selectors = [
                        "li.pager__item--next a",
                        "a.pager-next",
                        "a[title='Go to next page']",
                        "li.next a",
                        "//a[contains(text(), 'next') or contains(text(), 'Next')]"
                    ]
                    
                    for selector in next_button_selectors:
                        try:
                            if selector.startswith("//"):
                                next_btn = driver.find_element(By.XPATH, selector)
                            else:
                                next_btn = driver.find_element(By.CSS_SELECTOR, selector)
                            
                            if next_btn and next_btn.is_displayed():
                                next_btn.click()
                                time.sleep(3)  # Wait for page to load
                                log_message("Navigated to next page")
                                return True
                        except:
                            continue
                    
                    log_message("No next page button found or clickable")
                    return False
                except Exception as e:
                    log_message(f"Error navigating to next page: {str(e)}")
                    return False
            
            def refresh_page_and_find_table():
                """Refresh the page and find the redirect table"""
                try:
                    driver.refresh()
                    time.sleep(3)
                    
                    # Try multiple selectors to find table
                    table_selectors = [
                        "table.redirect-list",
                        "table.views-table",
                        "table.striped",
                        "table tbody",
                        "table"
                    ]
                    
                    for selector in table_selectors:
                        try:
                            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                            log_message(f"Found table after refresh with selector: {selector}")
                            return True
                        except:
                            continue
                    
                    return False
                except Exception as e:
                    log_message(f"Error refreshing page: {str(e)}")
                    return False
            
            def get_redirect_rows():
                """Get all redirect rows from current page"""
                try:
                    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr, .views-table tbody tr")
                    # Filter out empty or header rows
                    rows = [row for row in rows if row.get_attribute("innerHTML").strip() != ""]
                    return rows
                except Exception as e:
                    log_message(f"Error getting redirect rows: {str(e)}")
                    return []
            
            # Main processing loop
            current_page = 1
            pointer_row_index = 0  # Start from first row
            max_edits = 50  # Maximum edits before refresh check
            edits_counter = 0
            should_refresh = True  # Flag to control when to refresh
            
            # Estimated total for progress calculation: 50 pages × 50 rows = 2500
            estimated_total_redirects = 2500
            
            while True:
                
                # Refresh page if needed (first time or after successful edit)
                if should_refresh:
                    if not refresh_page_and_find_table():
                        driver.get(redirect_url)
                        time.sleep(3)
                        # Reset pointer to top after reload
                        pointer_row_index = 0
                
                # Get rows from current page
                rows = get_redirect_rows()
                
                if not rows or len(rows) == 0:
                    
                    # Check if there are more pages
                    if is_last_page():
                        break
                    else:
                        # Navigate to next page
                        if navigate_to_next_page():
                            current_page += 1
                            pointer_row_index = 0  # Reset pointer for new page
                            should_refresh = True
                            continue
                        else:
                            break
                
                
                # Process rows starting from pointer position
                for i in range(pointer_row_index, len(rows)):
                    row_start_time = time.time()
                    
                    # Calculate progress based on estimated total (50 pages × 50 rows = 2500)
                    progress_percentage = min(95, 5 + (total_processed / estimated_total_redirects * 90))
                    progress_bar.progress(int(progress_percentage))
                    status_text.text(f"Batch {current_page}, Redirect {i+1}/{len(rows)}")
                    progress_text.text(f"Progress: {int(progress_percentage)}%")
                    
                    try:
                        row = rows[i]
                        
                        # Get cells from the row
                        cells = []
                        try:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if not cells:
                                cells = row.find_elements(By.CSS_SELECTOR, "td")
                        except:
                            continue
                        
                        if len(cells) < 3:
                            continue
                        
                        # Extract source path and status code
                        source_path = ""
                        status_code = ""
                        
                        for idx, cell in enumerate(cells):
                            cell_text = cell.text.strip()
                            if cell_text in ["302", "301", "307"]:
                                status_code = cell_text
                            elif cell_text.startswith("/") or "http" in cell_text:
                                source_path = cell_text.split("\n")[0]
                        
                        # Fallback: use positional logic
                        if not status_code and len(cells) > 2:
                            status_code = cells[2].text.strip()
                        if not source_path and len(cells) > 0:
                            source_path = cells[0].text.strip().split("\n")[0]
                        
                        # Only process 302 redirects
                        if status_code != "302" or not source_path:
                            continue
                        
                        
                        # Find edit link
                        edit_link = None
                        try:
                            # Try multiple ways to find edit link
                            edit_link = row.find_element(By.LINK_TEXT, "Edit")
                        except:
                            try:
                                edit_link = row.find_element(By.PARTIAL_LINK_TEXT, "Edit")
                            except:
                                try:
                                    edit_link = row.find_element(By.CSS_SELECTOR, "a[href*='edit']")
                                except:
                                    try:
                                        edit_link = row.find_element(By.XPATH, ".//a[contains(@href, 'edit')]")
                                    except:
                                        try:
                                            # Try Arabic edit button
                                            edit_link = row.find_element(By.PARTIAL_LINK_TEXT, "تعديل")
                                        except:
                                            log_message(f"Could not find edit link for {source_path}")
                                            continue
                        
                        if not edit_link:
                            log_message(f"No edit link found for {source_path}")
                            continue
                        
                        # Store current window handle
                        main_window = driver.current_window_handle
                        
                        # Open edit page in new tab
                        edit_url = edit_link.get_attribute('href')
                        driver.execute_script(f"window.open('{edit_url}', '_blank');")
                        
                        # Switch to new tab
                        new_window = [window for window in driver.window_handles if window != main_window][0]
                        driver.switch_to.window(new_window)
                        time.sleep(2)
                        
                        # Find status code dropdown
                        status_select = None
                        status_selectors = [
                            "#edit-status-code",
                            "select[name*='status']",
                            "select[id*='status']",
                            "select[name*='code']",
                            "//select[contains(@name, 'status')]"
                        ]
                        
                        for selector in status_selectors:
                            try:
                                if selector.startswith("//"):
                                    status_select = driver.find_element(By.XPATH, selector)
                                else:
                                    status_select = driver.find_element(By.CSS_SELECTOR, selector)
                                if status_select:
                                    break
                            except:
                                continue
                        
                        if not status_select:
                            log_message(f"Status dropdown not found for {source_path}")
                            driver.close()
                            driver.switch_to.window(main_window)
                            continue
                        
                        # Check current value
                        current_value = status_select.get_attribute('value')
                        if current_value != "302":
                            log_message(f"Status already {current_value} for {source_path}")
                            driver.close()
                            driver.switch_to.window(main_window)
                            continue
                        
                        # Change to 301
                        try:
                            select = Select(status_select)
                            select.select_by_value("301")
                            
                            # Find and click save button
                            save_button = None
                            save_button_selectors = [
                                "#edit-submit",
                                "input[type='submit'][value*='Save']",
                                "input[type='submit'][value*='حفظ']",
                                "button[type='submit']",
                                "input[type='submit']",
                                "//input[@type='submit']"
                            ]
                            
                            for selector in save_button_selectors:
                                try:
                                    if selector.startswith("//"):
                                        save_button = driver.find_element(By.XPATH, selector)
                                    else:
                                        save_button = driver.find_element(By.CSS_SELECTOR, selector)
                                    if save_button:
                                        break
                                except:
                                    continue
                            
                            if not save_button:
                                raise Exception("Save button not found")
                            
                            save_button.click()
                            time.sleep(3)  # Wait for save
                            
                            # Check if save was successful
                            final_url = driver.current_url
                            
                            if "/admin/config/search/redirect" in final_url and "edit" not in final_url:
                                # SUCCESSFUL EDIT
                                row_time = time.time() - row_start_time
                                
                                # Close edit tab
                                driver.close()
                                driver.switch_to.window(main_window)
                                
                                # Update counters
                                total_fixed += 1
                                total_processed += 1
                                edits_counter += 1
                                local_operation_times.append(row_time)  # Add time to operation times
                                
                                # Log success
                                success_msg = f"✅ [{total_processed}] Fixed redirect: {source_path} (Execution time: {format_time(row_time)})"
                                st.success(success_msg)
                                log_message(success_msg)
                                
                                # SUCCESS LOGIC: Refresh parent page and stay on same position
                                should_refresh = True
                                # Pointer stays at same index because page will refresh
                                break  # Exit for-loop to process same position on refreshed page
                                
                            else:
                                # EDIT FAILED - Save not successful
                                row_time = time.time() - row_start_time
                                
                                # Close edit tab
                                driver.close()
                                driver.switch_to.window(main_window)
                                
                                # Log failure
                                error_msg = f"❌ [{total_processed + 1}] Failed to save: {source_path} (Execution time: {format_time(row_time)})"
                                st.error(error_msg)
                                log_message(error_msg)
                                
                                total_processed += 1
                                local_operation_times.append(row_time)  # Add time to operation times for failures too
                                local_failures.append({
                                    "URL": source_path,
                                    "Status Code": "302",
                                    "Error": "Failed to save due to infinity loop",
                                })
                                
                                # FAILURE LOGIC: Move pointer to next row, don't refresh
                                pointer_row_index = i + 1
                                should_refresh = False
                                # Continue to next row
                                continue
                                
                        except Exception as save_error:
                            row_time = time.time() - row_start_time
                            error_msg = f"❌ [{total_processed + 1}] Error saving: {source_path} - {str(save_error)[:100]} (Execution time: {format_time(row_time)})"
                            st.error(error_msg)
                            log_message(error_msg)
                            
                            # Close tab if still open
                            try:
                                driver.close()
                                driver.switch_to.window(main_window)
                            except:
                                if driver.window_handles:
                                    driver.switch_to.window(driver.window_handles[0])
                            
                            total_processed += 1
                            local_operation_times.append(row_time)  # Add time to operation times for failures too
                            local_failures.append({
                                "URL": source_path,
                                "Status Code": "302",
                                "Error": "Failed to save due to infinity loop",
                            })
                            
                            # Move pointer to next row, don't refresh
                            pointer_row_index = i + 1
                            should_refresh = False
                            continue
                            
                    except Exception as row_error:
                        row_time = time.time() - row_start_time
                        error_msg = f"❌ [{total_processed + 1}] Row processing error: {str(row_error)[:100]} (Execution time: {format_time(row_time)})"
                        st.error(error_msg)
                        log_message(error_msg)
                        
                        # Try to get source_path if available, otherwise use empty string
                        source_path_error = source_path if 'source_path' in locals() else "Unknown URL"
                        
                        total_processed += 1
                        local_operation_times.append(row_time)  # Add time to operation times for failures too
                        local_failures.append({
                            "URL": source_path_error,
                            "Status Code": "302",
                            "Error": "Failed to save due to infinity loop",
                        })
                        
                        # Move pointer to next row, don't refresh
                        pointer_row_index = i + 1
                        should_refresh = False
                        continue
                
                # Check if we've processed all rows on current page
                if pointer_row_index >= len(rows):
                    # Check if we've reached max edits
                    if edits_counter >= max_edits:
                        should_refresh = True
                        edits_counter = 0
                        continue
                    
                    # Check if there are more pages
                    if is_last_page():
                        break
                    else:
                        # Navigate to next page
                        if navigate_to_next_page():
                            current_page += 1
                            pointer_row_index = 0  # Reset to top of new page
                            should_refresh = True
                        else:
                            break
                else:
                    # We haven't finished current page, continue with next iteration
                    continue
            
            # Final progress update
            progress_bar.progress(100)
            progress_text.text("Progress: 100%")
            
            # CRITICAL FIX: Update the parent function's tracking variables
            success_count[0] = total_fixed  # Update success count
            operation_times.extend(local_operation_times)  # Add ALL operation times (success + failure)
            failures.extend(local_failures)  # Add failures to main failures list
            
            # CRITICAL FIX: Mark rows as processed for summary calculation
            # For redirect fix, we need to track processed count
            for i in range(total_processed):
                processed_rows.add(f"redirect_{i}")  # Add unique identifier for each processed redirect
            
            # Display failure report only if there are failures
            if local_failures:
                failure_df = pd.DataFrame(local_failures)
            
            return  # Exit early for redirect fix task
            
        except Exception as e:
            error_msg = f"❌ Fatal error in redirect fix: {str(e)}"
            st.error(error_msg)
            log_message(error_msg)
            return  # Exit on fatal error
            
    for index, row in epoch_df.iterrows():
        row_start_time = time.time()
        row_time = 0  
        try:
            if task_type == "URL redirection":
                original_url = row['URL'].strip()
                to_url = row['URL Redirection'].strip()
                if use_epochs:
                    row_num = epoch_df.index.get_loc(index) + 1
                    total_rows_in_epoch = len(epoch_df)
                    overall_row_num = (epoch_idx * EPOCH_SIZE) + row_num
                    status_text.text(f"Epoch {epoch_idx + 1}/{total_epochs}, URL: {row_num}/{total_rows_in_epoch} (Overall: {overall_row_num}/{total_rows}) - {original_url}")
                else:
                    status_text.text(f"Processing redirection {index+1}/{total_rows}: {original_url}")
                current_progress[0] = min(current_progress[0] + progress_increment * 0.2, 100)
                progress_bar.progress(int(current_progress[0]))
                progress_text.text(f"Progress: {int(current_progress[0])}%{' (Epoch {}/{})'.format(epoch_idx + 1, total_epochs) if use_epochs else ''}")
                redirect_url = f"{base_url}/admin/config/search/redirect/add"
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(redirect_url)
                path_url_slug = slugify_alias(original_url, redirection=True, path_url_slug=True)
                path_to_slug = slugify_alias(to_url, redirection=True, path_to_slug=True)
                path_url_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-redirect-source-0-path')))
                to_url_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-redirect-redirect-0-uri')))
                driver.execute_script("arguments[0].value = '';", path_url_input)
                driver.execute_script("arguments[0].value = arguments[1];", path_url_input, f'{path_url_slug}')
                driver.execute_script("arguments[0].value = '';", to_url_input)
                driver.execute_script("arguments[0].value = arguments[1];", to_url_input, f'{path_to_slug}')
                current_progress[0] = min(current_progress[0] + progress_increment * 0.4, 100)
                progress_bar.progress(int(current_progress[0]))
                progress_text.text(f"Progress: {int(current_progress[0])}%{' (Epoch {}/{})'.format(epoch_idx + 1, total_epochs) if use_epochs else ''}")
                if click_save_button(driver, wait, website_name, website_lang, False):
                    row_time = time.time() - row_start_time
                    operation_times.append(row_time)
                    success_count[0] += 1
                    processed_rows.add(index)
                    success_msg = f"✅ [{index+1}] Updated URL redirection: {original_url} (Execution time: {format_time(row_time)})"
                    st.success(success_msg)
                    log_message(success_msg)
                else:
                    raise Exception("Failed to save redirection!")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                current_progress[0] = min(current_progress[0] + progress_increment * 0.4, 100)
                progress_bar.progress(int(current_progress[0]))
                progress_text.text(f"Progress: {int(current_progress[0])}%{' (Epoch {}/{})'.format(epoch_idx + 1, total_epochs) if use_epochs else ''}")
                status_text.text(f"Completed redirection {index+1}/{total_rows}")
            
            else:
                original_url = row['URL'].strip()
                url_path = slugify_url(original_url)
                if '/en' not in base_url and '/ar' not in base_url:
                    base_url = get_base_url(base_url)
                full_url = f"{base_url}{url_path}"
                if use_epochs:
                    row_num = epoch_df.index.get_loc(index) + 1
                    total_rows_in_epoch = len(epoch_df)
                    overall_row_num = (epoch_idx * EPOCH_SIZE) + row_num
                    status_text.text(f"Epoch {epoch_idx + 1}/{total_epochs}, URL: {row_num}/{total_rows_in_epoch} (Overall: {overall_row_num}/{total_rows}) - {original_url}")
                else:
                    status_text.text(f"Processing {index+1}/{total_rows}: {original_url}")
                current_progress[0] = min(current_progress[0] + progress_increment * 0.2, 100)
                progress_bar.progress(int(current_progress[0]))
                progress_text.text(f"Progress: {int(current_progress[0])}%{' (Epoch {}/{})'.format(epoch_idx + 1, total_epochs) if use_epochs else ''}")
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                try:
                    driver.get(full_url)
                    if get_website_name(website_name) == "Nestlé Mena":
                        time.sleep(5) 
                        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    else:
                        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))   
                except Exception as e:
                    raise Exception(f"Failed to load page!")
                
                # Edit phase
                if get_website_name(website_name) in ["Nestlé Professional"]:
                    if website_lang in ["Arabic", "English"]:
                        edit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'nav-link') and contains(text(), 'Edit')]")))
                        driver.execute_script("arguments[0].click();", edit_button)
                    elif website_lang == "French":
                        edit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'nav-link') and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'modifier')]")))
                        driver.execute_script("arguments[0].click();", edit_button)
                elif get_website_name(website_name) in ["Nestlé Mena"]:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav.tabs")))
                    edit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav[contains(@class, 'tabs')]//a[contains(@href, '/edit')]")))
                    driver.execute_script("arguments[0].click();", edit_button)   
                elif get_website_name(website_name) in ["Nestlé Family Nes"]:
                    try:
                        edit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//li/a[contains(@href, '/edit') and text()='Edit']")))
                        driver.execute_script("arguments[0].click();", edit_button)
                    except:
                        try:
                            task_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Local Tasks']")))
                            driver.execute_script("arguments[0].click();", task_button)
                            time.sleep(0.5)
                            edit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//li/a[contains(@href, '/edit') and text()='Edit']")))
                            driver.execute_script("arguments[0].click();", edit_button)
                        except Exception as e:
                            raise Exception(f"Failed to access edit page via Tasks button!")
                elif get_website_name(website_name) in ["Nestlé Family"]:
                        try:
                            body_element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.TAG_NAME, "body"))
                            )
                            node_id = body_element.get_attribute("data-node")
                            edit_url = f'{base_url}/{website_lang[:2].lower()}/node/{node_id}/edit'
                            driver.get(edit_url)
                        except Exception as e:
                            raise Exception(f"Failed to access edit page via Tasks button!")
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
                            raise Exception(f"Failed to access edit page via Tasks button!")
                    else:
                        if get_website_name(website_name) in ["Nestlé for Healthier Kids"]:
                            try:
                                edit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.nav-link[href*='/edit']")))
                                driver.execute_script("arguments[0].click();", edit_button)
                            except Exception as e:
                                raise Exception(f"Failed to access edit page via link text!")  
                        else :      
                            try:
                                edit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.moderation-sidebar-link.button[href*='edit']")))
                                driver.execute_script("arguments[0].click();", edit_button)
                            except Exception as e:
                                raise Exception(f"Failed to access edit page via link text!")    
                progress_text.text(f"Progress: {int(current_progress[0])}%{' (Epoch {}/{})'.format(epoch_idx + 1, total_epochs) if use_epochs else ''}")
                
                is_taxonomy = "/taxonomy" in driver.current_url
                if task_type == "Add H1":
                    try:
                        header_value  = row['H1']
                        if is_taxonomy:
                            header_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-name-0-value')))
                        else:
                            header_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-title-0-value')))
                        if get_website_name(website_name) in ["Nestlé Family Nes"]:
                            if is_taxonomy:
                                header_input.clear()
                                header_input.send_keys(header_value)   
                            else :
                                driver.execute_script("arguments[0].value = '';",header_input )
                                driver.execute_script("arguments[0].value = arguments[1];", header_input, header_value)   
                        else:     
                            driver.execute_script("arguments[0].value = '';",header_input )
                            driver.execute_script("arguments[0].value = arguments[1];", header_input, header_value)
                    
                    except:
                        raise Exception(f"Failed to add H1!")  
                    time.sleep(4)
                    if click_save_button(driver, wait, website_name, website_lang, is_taxonomy):
                        row_time = time.time() - row_start_time
                        operation_times.append(row_time)
                        success_count[0] += 1
                        processed_rows.add(index)
                        success_msg = f"✅ [{index+1}] Updated H1: {full_url} (Execution time: {format_time(row_time)})"
                        st.success(success_msg)
                        log_message(success_msg)
                    else:
                        raise Exception("Failed to save Add H1 changes!")   
                        
                elif task_type == "URL update":
                    try:
                        new_alias = slugify_alias(row['New URL Structure'])
                        if is_taxonomy:
                            try :
                                alias_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-field-metatags-0-advanced-canonical-url')))
                            except :
                                alias_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-path-0-alias')))    
                        else:
                            alias_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-path-0-alias')))
                        if get_website_name(website_name) in ["Nestlé Family Nes"]:
                            if is_taxonomy:
                                alias_input.clear()
                                alias_input.send_keys(new_alias)   
                            else:
                                driver.execute_script("arguments[0].value = '';", alias_input)
                                driver.execute_script("arguments[0].value = arguments[1];", alias_input, f'{new_alias}')      
                        else:     
                            driver.execute_script("arguments[0].value = '';", alias_input)
                            driver.execute_script("arguments[0].value = arguments[1];", alias_input, f'{new_alias}')   
                    except Exception as e:
                        raise Exception(f"Failed to update URL alias!")
                    if click_save_button(driver, wait, website_name, website_lang, is_taxonomy):
                        row_time = time.time() - row_start_time
                        operation_times.append(row_time)
                        success_count[0] += 1
                        processed_rows.add(index)
                        success_msg = f"✅ [{index+1}] Updated alias: {full_url} → {base_url}/{website_lang[:2].lower()}/{new_alias} (Execution time: {format_time(row_time)})"
                        st.success(success_msg)
                        log_message(success_msg)
                    else:
                        raise Exception("Failed to save URL alias changes!")
                        
                elif task_type == "Meta title":
                    meta_title = row['Meta Title']
                    if get_website_name(website_name) == "Nestlé Family Nes":
                        if not try_open_metatags_dropdown_mom_and_me(driver, wait):
                                raise Exception("Failed to open meta tags!")
                        update_meta_title_mom_and_me(driver, wait, meta_title)
                        time.sleep(1)
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(0.5)
                        try:
                            driver.find_element(By.XPATH, '//input[@value="Save"]').click()
                            time.sleep(1)
                            try:
                                wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Save"]')))
                            except:
                                pass
                        except:
                            driver.find_element(By.XPATH, '//input[@value="حفظ"]').click()
                            time.sleep(1)
                            try:
                                wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="حفظ"]')))
                            except:
                                pass    

                        if click_save_button_mom_and_me(driver, wait):
                            row_time = time.time() - row_start_time
                            operation_times.append(row_time)
                            success_count[0] += 1
                            processed_rows.add(index)
                            success_msg = f"✅ [{index+1}] Updated meta title: {full_url} (Execution time: {format_time(row_time)})"
                            st.success(success_msg)
                            log_message(success_msg)
                        else:
                            raise Exception("Failed to save meta title!")
                    else:
                        if not try_open_metatags_dropdown(wait, driver, website_name):
                            try:
                                if is_taxonomy:
                                    driver.get(f"{driver.current_url}#edit-field-metatags-0")
                                else:
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
                                        
                                
                                    
                            except Exception as fallback_e:
                                raise Exception("Failed to access meta fields!")
                        short_wait = WebDriverWait(driver, SHORT_WAIT)
                        title_input = None
                        if is_taxonomy:
                            try:
                                title_input = short_wait.until(EC.presence_of_element_located((By.ID, "edit-field-metatags-0-basic-title")))
                            except:
                                raise Exception("Failed to locate meta title field in taxonomy flow!")
                        else:
                            for title_selector in ["#edit-field-meta-tags-0-basic-title", "#edit-field-ln-n-meta-tags-0-basic-title"]:
                                try:
                                    title_input = short_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, title_selector)))
                                    break
                                except:
                                    continue
                        if not title_input:
                            raise Exception("Failed to locate meta title field!")
                        driver.execute_script("arguments[0].value = '';", title_input)
                        driver.execute_script("arguments[0].value = arguments[1];", title_input, meta_title)
                        if click_save_button(driver, wait, website_name, website_lang, is_taxonomy):
                            row_time = time.time() - row_start_time
                            operation_times.append(row_time)
                            success_count[0] += 1
                            processed_rows.add(index)
                            success_msg = f"✅ [{index+1}] Updated meta title: {full_url} (Execution time: {format_time(row_time)})"
                            st.success(success_msg)
                            log_message(success_msg)
                        else:
                            raise Exception("Failed to save meta title changes!")
                            
                elif task_type == "Meta description":
                    meta_desc = row['Meta Description']
                    if get_website_name(website_name) == "Nestlé Family Nes":
                        if not try_open_metatags_dropdown_mom_and_me(driver, wait):
                            raise Exception("Failed to open meta tags!")
                        update_meta_description_mom_and_me(driver, wait, meta_desc)
                        try:
                            driver.find_element(By.XPATH, '//input[@value="Save"]').click()
                            time.sleep(1)
                            try:
                                wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Save"]')))
                            except:
                                pass
                        except:
                            driver.find_element(By.XPATH, '//input[@value="حفظ"]').click()
                            time.sleep(1)
                            try:
                                wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="حفظ"]')))
                            except:
                                pass  

                        if click_save_button_mom_and_me(driver, wait):
                            row_time = time.time() - row_start_time
                            operation_times.append(row_time)
                            success_count[0] += 1
                            processed_rows.add(index)
                            success_msg = f"✅ [{index+1}] Updated meta description: {full_url} (Execution time: {format_time(row_time)})"
                            st.success(success_msg)
                            log_message(success_msg)
                        else:
                            raise Exception("Failed to save meta description!")
                    else:
                        if not try_open_metatags_dropdown(wait, driver, website_name):
                            try:
                                if is_taxonomy:
                                    driver.get(f"{driver.current_url}#edit-field-metatags-0")
                                else:
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

                                    
                                    
                            except Exception as fallback_e:
                                raise Exception("Failed to access meta fields!")
                        short_wait = WebDriverWait(driver, SHORT_WAIT)
                        desc_input = None
                        if is_taxonomy:
                            try:
                                desc_input = short_wait.until(EC.presence_of_element_located((By.ID, "edit-field-metatags-0-basic-description")))
                            except:
                                raise Exception("Failed to locate meta description field in taxonomy flow!")
                        else:
                            for desc_selector in ["#edit-field-meta-tags-0-basic-description", "#edit-field-ln-n-meta-tags-0-basic-description"]:
                                try:
                                    desc_input = short_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, desc_selector)))
                                    break
                                except:
                                    continue
                        if not desc_input:
                            raise Exception("Failed to locate meta description field!")
                        driver.execute_script("arguments[0].value = '';", desc_input)
                        driver.execute_script("arguments[0].value = arguments[1];", desc_input, meta_desc)
                        if click_save_button(driver, wait, website_name, website_lang, is_taxonomy):
                            row_time = time.time() - row_start_time
                            operation_times.append(row_time)
                            success_count[0] += 1
                            processed_rows.add(index)
                            success_msg = f"✅ [{index+1}] Updated meta description: {full_url} (Execution time: {format_time(row_time)})"
                            st.success(success_msg)
                            log_message(success_msg)
                        else:
                            raise Exception("Failed to save meta description changes!")
                elif task_type == "Meta title + description":
                    meta_title = row['Meta Title']
                    meta_desc = row['Meta Description']
                    if get_website_name(website_name) == "Nestlé Family Nes":
                        if not try_open_metatags_dropdown_mom_and_me(driver, wait):
                            raise Exception("Failed to open meta tags!")
                        update_meta_title_mom_and_me(driver, wait, meta_title)
                        update_meta_description_mom_and_me(driver, wait, meta_desc)
                        try:
                            driver.find_element(By.XPATH, '//input[@value="Save"]').click()
                            time.sleep(1)
                            try:
                                wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Save"]')))
                            except:
                                pass
                        except:
                            driver.find_element(By.XPATH, '//input[@value="حفظ"]').click()
                            time.sleep(1)
                            try:
                                wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="حفظ"]')))
                            except:
                                pass  

                        if click_save_button_mom_and_me(driver, wait):
                            row_time = time.time() - row_start_time
                            operation_times.append(row_time)
                            success_count[0] += 1
                            processed_rows.add(index)
                            success_msg = f"✅ [{index+1}] Updated meta title + description: {full_url} (Execution time: {format_time(row_time)})"
                            st.success(success_msg)
                            log_message(success_msg)
                        else:
                            raise Exception("Failed to save meta title + description!")
                    else:
                        if not try_open_metatags_dropdown(wait, driver, website_name):
                            try:
                                if is_taxonomy:
                                    driver.get(f"{driver.current_url}#edit-field-metatags-0")
                                else:
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
                                        
                                
                                    
                                    
                            except Exception as fallback_e:
                                raise Exception("Failed to access meta fields!")
                        short_wait = WebDriverWait(driver, SHORT_WAIT)
                        title_input = None
                        desc_input = None
                        if is_taxonomy:
                            try:
                                title_input = short_wait.until(EC.presence_of_element_located((By.ID, "edit-field-metatags-0-basic-title")))
                                desc_input = short_wait.until(EC.presence_of_element_located((By.ID, "edit-field-metatags-0-basic-description")))
                            except:
                                raise Exception("Failed to locate meta title or description field in taxonomy flow!")
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
                            raise Exception("failed to locate meta title or description field!")
                        driver.execute_script("arguments[0].value = '';", title_input)
                        driver.execute_script("arguments[0].value = arguments[1];", title_input, meta_title)
                        driver.execute_script("arguments[0].value = '';", desc_input)
                        driver.execute_script("arguments[0].value = arguments[1];", desc_input, meta_desc)
                        if click_save_button(driver, wait, website_name, website_lang, is_taxonomy):
                            row_time = time.time() - row_start_time
                            operation_times.append(row_time)
                            success_count[0] += 1
                            processed_rows.add(index)
                            success_msg = f"✅ [{index+1}] Updated meta title + description: {full_url} (Execution time: {format_time(row_time)})"
                            st.success(success_msg)
                            log_message(success_msg)
                        else:
                            raise Exception("Failed to save meta title + description changes!")
                elif task_type == "Add H1 + meta title + description":
                    header_value  = row['H1']
                    meta_title = row['Meta Title']
                    meta_desc = row['Meta Description']
                    try:
                        if is_taxonomy:
                            header_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-name-0-value')))
                        else:
                            header_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-title-0-value')))
                        if get_website_name(website_name) in ["Nestlé Family Nes"]:
                            if is_taxonomy:
                                header_input.clear()
                                header_input.send_keys(header_value)   
                            else :
                                driver.execute_script("arguments[0].value = '';",header_input )
                                driver.execute_script("arguments[0].value = arguments[1];", header_input, header_value)   
                        else:     
                            driver.execute_script("arguments[0].value = '';",header_input )
                            driver.execute_script("arguments[0].value = arguments[1];", header_input, header_value)
                    
                    except:
                        raise Exception(f"Failed to add H1!")  
                    if get_website_name(website_name) == "Nestlé Family Nes":
                        if not try_open_metatags_dropdown_mom_and_me(driver, wait):
                            raise Exception("Failed to open meta tags!")
                        update_meta_title_mom_and_me(driver, wait, meta_title)
                        update_meta_description_mom_and_me(driver, wait, meta_desc)
                        try:
                            driver.find_element(By.XPATH, '//input[@value="Save"]').click()
                            time.sleep(1)
                            try:
                                wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Save"]')))
                            except:
                                pass
                        except:
                            driver.find_element(By.XPATH, '//input[@value="حفظ"]').click()
                            time.sleep(1)
                            try:
                                wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="حفظ"]')))
                            except:
                                pass  

                        if click_save_button_mom_and_me(driver, wait):
                            row_time = time.time() - row_start_time
                            operation_times.append(row_time)
                            success_count[0] += 1
                            processed_rows.add(index)
                            success_msg = f"✅ [{index+1}] Updated H1 + alias + meta title + description: {full_url} → {base_url}/{website_lang[:2].lower()}/{new_alias} (Execution time: {format_time(row_time)})"
                            st.success(success_msg)
                            log_message(success_msg)
                        else:
                            raise Exception("Failed to save H1 + alias + meta title + description!")
                    else:
                        if not try_open_metatags_dropdown(wait, driver, website_name):
                            try:
                                if is_taxonomy:
                                    driver.get(f"{driver.current_url}#edit-field-metatags-0")
                                else:
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
                                        


                                    
                            except Exception as fallback_e:
                                raise Exception("Failed to access meta fields")
                        short_wait = WebDriverWait(driver, SHORT_WAIT)
                        title_input = None
                        desc_input = None
                        if is_taxonomy:
                            try:
                                title_input = short_wait.until(EC.presence_of_element_located((By.ID, "edit-field-metatags-0-basic-title")))
                                desc_input = short_wait.until(EC.presence_of_element_located((By.ID, "edit-field-metatags-0-basic-description")))
                            except:
                                raise Exception("Failed to locate meta title or description field in taxonomy flow!")
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
                            raise Exception("Failed to locate meta title or description field!")
                        driver.execute_script("arguments[0].value = '';", title_input)
                        driver.execute_script("arguments[0].value = arguments[1];", title_input, meta_title)
                        driver.execute_script("arguments[0].value = '';", desc_input)
                        driver.execute_script("arguments[0].value = arguments[1];", desc_input, meta_desc)
                        if click_save_button(driver, wait, website_name, website_lang, is_taxonomy):
                            row_time = time.time() - row_start_time
                            operation_times.append(row_time)
                            success_count[0] += 1
                            processed_rows.add(index)
                            success_msg = f"✅ [{index+1}] Updated alias + meta title + description: {full_url} → {base_url}/{website_lang[:2].lower()}/{new_alias} (Execution time: {format_time(row_time)})"
                            st.success(success_msg)
                            log_message(success_msg)
                        else:
                            raise Exception("Failed to save H1 + meta title + description!")    
                                                
                elif task_type == "All":
                    header_value  = row['H1']
                    new_alias = slugify_alias(row['New URL Structure'])
                    meta_title = row['Meta Title']
                    meta_desc = row['Meta Description']
                    try:
                        if is_taxonomy:
                            header_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-name-0-value')))
                        else:
                            header_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-title-0-value')))
                        if get_website_name(website_name) in ["Nestlé Family Nes"]:
                            if is_taxonomy:
                                header_input.clear()
                                header_input.send_keys(header_value)   
                            else :
                                driver.execute_script("arguments[0].value = '';",header_input )
                                driver.execute_script("arguments[0].value = arguments[1];", header_input, header_value)   
                        else:     
                            driver.execute_script("arguments[0].value = '';",header_input )
                            driver.execute_script("arguments[0].value = arguments[1];", header_input, header_value)
                    
                    except:
                        raise Exception(f"Failed to add H1!")  
                    try:
                        new_alias = slugify_alias(row['New URL Structure'])
                        if is_taxonomy:
                            try :
                                alias_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-field-metatags-0-advanced-canonical-url')))
                            except :
                                alias_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-path-0-alias')))    
                        else:
                            alias_input = wait.until(EC.presence_of_element_located((By.ID, 'edit-path-0-alias')))
                        if get_website_name(website_name) in ["Nestlé Family Nes"]:
                            if is_taxonomy:
                                alias_input.clear()
                                alias_input.send_keys(new_alias)   
                            else:
                                driver.execute_script("arguments[0].value = '';", alias_input)
                                driver.execute_script("arguments[0].value = arguments[1];", alias_input, f'{new_alias}')      
                        else:     
                            driver.execute_script("arguments[0].value = '';", alias_input)
                            driver.execute_script("arguments[0].value = arguments[1];", alias_input, f'{new_alias}')   
                    except Exception as e:
                        raise Exception(f"Failed to update URL alias!")
                    if get_website_name(website_name) == "Nestlé Family Nes":
                        if not try_open_metatags_dropdown_mom_and_me(driver, wait):
                            raise Exception("Failed to open meta tags!")
                        update_meta_title_mom_and_me(driver, wait, meta_title)
                        update_meta_description_mom_and_me(driver, wait, meta_desc)
                        try:
                            driver.find_element(By.XPATH, '//input[@value="Save"]').click()
                            time.sleep(1)
                            try:
                                wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Save"]')))
                            except:
                                pass
                        except:
                            driver.find_element(By.XPATH, '//input[@value="حفظ"]').click()
                            time.sleep(1)
                            try:
                                wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="حفظ"]')))
                            except:
                                pass  
                        if click_save_button_mom_and_me(driver, wait):
                            row_time = time.time() - row_start_time
                            operation_times.append(row_time)
                            success_count[0] += 1
                            processed_rows.add(index)
                            success_msg = f"✅ [{index+1}] Updated H1 + alias + meta title + description: {full_url} → {base_url}/{website_lang[:2].lower()}/{new_alias} (Execution time: {format_time(row_time)})"
                            st.success(success_msg)
                            log_message(success_msg)
                        else:
                            raise Exception("Failed to save H1 + alias + meta title + description!")
                    else:
                        if not try_open_metatags_dropdown(wait, driver, website_name):
                            try:
                                if is_taxonomy:
                                    driver.get(f"{driver.current_url}#edit-field-metatags-0")
                                else:
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
                                        


                                    
                                    
                            except Exception as fallback_e:
                                raise Exception("Failed to access meta fields")
                        short_wait = WebDriverWait(driver, SHORT_WAIT)
                        title_input = None
                        desc_input = None
                        if is_taxonomy:
                            try:
                                title_input = short_wait.until(EC.presence_of_element_located((By.ID, "edit-field-metatags-0-basic-title")))
                                desc_input = short_wait.until(EC.presence_of_element_located((By.ID, "edit-field-metatags-0-basic-description")))
                            except:
                                raise Exception("Failed to locate meta title or description field in taxonomy flow!")
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
                            raise Exception("Failed to locate meta title or description field!")
                        driver.execute_script("arguments[0].value = '';", title_input)
                        driver.execute_script("arguments[0].value = arguments[1];", title_input, meta_title)
                        driver.execute_script("arguments[0].value = '';", desc_input)
                        driver.execute_script("arguments[0].value = arguments[1];", desc_input, meta_desc)
                        if click_save_button(driver, wait, website_name, website_lang, is_taxonomy):
                            row_time = time.time() - row_start_time
                            operation_times.append(row_time)
                            success_count[0] += 1
                            processed_rows.add(index)
                            success_msg = f"✅ [{index+1}] Updated alias + meta title + description: {full_url} → {base_url}/{website_lang[:2].lower()}/{new_alias} (Execution time: {format_time(row_time)})"
                            st.success(success_msg)
                            log_message(success_msg)
                        else:
                            raise Exception("Failed to save H1 + alias + meta title + description!")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                current_progress[0] = min(current_progress[0] + progress_increment * 0.6, 100)
                progress_bar.progress(int(current_progress[0]))
                progress_text.text(f"Progress: {int(current_progress[0])}%{' (Epoch {}/{})'.format(epoch_idx + 1, total_epochs) if use_epochs else ''}")
                status_text.text(f"Completed {index+1}/{total_rows}")
        except Exception as e:
            row_time = time.time() - row_start_time
            error_msg = f"❌ [{index+1}] Error with {row.get('URL', '')}!"
            st.error(error_msg)
            log_message(error_msg)
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
    # Initialize session state for OTP handling
    if 'otp_submitted' not in st.session_state:
        st.session_state.otp_submitted = {}
    if 'otp_values' not in st.session_state:
        st.session_state.otp_values = {}

    # Clear previous logs
    automation_logs.clear()
    
    base_url = get_base_url(website_name)
    start_msg = f"✅ Starting automation for: {website_name} ({website_lang}, {task_type})"
    st.success(start_msg)
    log_message(start_msg)
    
    all_failures = []
    total_start_time = time.time()
    all_operation_times = []
    total_success_count = [0]  # Use list to allow modification in nested function
    total_count = 0
    processed_rows = set()  # Track processed rows

    websitename = get_website_name(website_name)
    use_epochs = (
    websitename in ["Nestlé Professional", "Nestlé Family Nes"]
    or show_nestle_mena
    )

    try:
        if task_type == "Upload images with alt text":
            image_paths = save_uploaded_images(images_uploaded)
            info_msg = f"Saved and converted {len(image_paths)} images to JPG format"
            st.info(info_msg)
            log_message(info_msg)
            
            total_images = len(image_paths)
            total_count = total_images
            current_progress = [0]  # Use list to allow modification
            
            # Initialize progress tracking
            progress_bar.progress(0)
            status_text.text(f"Preparing to upload {total_images} images...")
            progress_text.text("Progress: 0%")
            
            alt_texts = {}
            if 'Image Name' in df.columns and 'Alt Text' in df.columns:
                alt_texts = dict(zip(df['Image Name'], df['Alt Text']))
            else:
                warning_msg = "No alt text data found in the dataframe. Using image names as alt text."
                st.warning(warning_msg)
                log_message(warning_msg)
                alt_texts = {os.path.basename(path): os.path.basename(path).split('.')[0] for path in image_paths}

            driver = initialize_driver()
            wait = WebDriverWait(driver, LONG_WAIT)
            try:
                perform_login(driver, wait, website_name, website_lang, username, password, otp_code, show_shield, shield_username, shield_password, show_nestle_mena, show_nestle_family, otp)
                
                success_count = 0
                failures = []
                all_operation_times = []
                
                for i, image_path in enumerate(image_paths):
                    image_start_time = time.time()
                    image_name = os.path.basename(image_path)
                    try:
                        # Update progress
                        progress = int((i / total_images) * 100)
                        current_progress[0] = progress
                        progress_bar.progress(progress)
                        status_text.text(f"Uploading image {i+1}/{total_images}: {image_name}")
                        progress_text.text(f"Progress: {progress}%")
                        
                        upload_url = f"{base_url}/{'media/add/image' if show_no_lang else 'en/media/add/image'}"
                        driver.execute_script("window.open('');")
                        driver.switch_to.window(driver.window_handles[1])
                        driver.get(upload_url)
                        
                        file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file' and @accept='image/*']")))
                        file_input.send_keys(image_path)
                        
                        # Wait for upload to complete
                        time.sleep(2)  # Adjust based on your network speed
                        
                        # Fill in details
                        name_field = wait.until(EC.presence_of_element_located((By.ID, 'edit-name-0-value')))
                        name_field.clear()
                        name_field.send_keys(os.path.splitext(image_name)[0])
                        
                        alt_text = alt_texts.get(image_name, os.path.splitext(image_name)[0])
                        alt_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id, 'edit-field-media-image-0-alt')]")))
                        alt_field.clear()
                        alt_field.send_keys(alt_text)
                        
                        if click_save_button(driver, wait, website_name, website_lang, False):
                            image_time = time.time() - image_start_time
                            all_operation_times.append(image_time)
                            success_count += 1
                            success_msg = f"✅ Successfully uploaded {image_name} (Time: {format_time(image_time)})"
                            st.success(success_msg)
                            log_message(success_msg)
                        else:
                            raise Exception("Failed to save image upload!")
                        
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        
                    except Exception as e:
                        image_time = time.time() - image_start_time
                        error_msg = f"❌ Failed to upload {image_name}: {str(e)}"
                        st.error(error_msg)
                        log_message(error_msg)
                        failures.append({'Image': image_name, 'Error': str(e)})
                        if len(driver.window_handles) > 1:
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                        continue
                
                # Final progress update
                progress_bar.progress(100)
                status_text.text(f"Completed {total_images} image uploads")
                progress_text.text("Progress: 100%")
                
                # Update main tracking variables
                total_success_count[0] = success_count
                all_failures.extend(failures)
                
                # Generate summary
                total_time = time.time() - total_start_time
                avg_time = sum(all_operation_times) / len(all_operation_times) if all_operation_times else 0
                success_percentage = int((success_count / total_images) * 100) if total_images > 0 else 0
                

                
                summary_message = (
                    f"**📦 Image Upload Summary**\n\n"
                    f"**Total automation execution time:** {format_time(total_time)}<br>"
                    f"**Average automation time per operation:** {format_time(avg_time)}<br>"
                    f"**Total images processed:** {total_images}<br>"
                    f"**Successfully uploaded:** {success_count} ({success_percentage}%)<br>"
                    f"**Failed uploads:** {len(failures)}<br>"
                    f"**Incomplete:** {total_images - success_count - len(failures)}<br>"
                )
                
                st.success(summary_message)
                log_message(summary_message)
                
                # Save automation logs
                log_file_path = save_automation_log(website_name, website_lang, summary_message, automation_logs)
                if log_file_path:
                    st.info(f"📄 Automation log saved to: {log_file_path}")
                if failures:
                    fail_df = pd.DataFrame(failures)
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        fail_df.to_excel(writer, index=False, sheet_name='Upload Failures')
                    output.seek(0)
                    
                    # Create the file path for the failure report
                    failure_report_filename = f"{get_website_name(website_name)}_Image_Upload_Failures.xlsx"
                    
                    st.success("Failure report generated successfully!")
                    
                    st.download_button(
                        label="Download Failures Report",
                        data=output,
                        file_name=failure_report_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                st.stop()
                
            except Exception as e:
                error_msg = f"❌ Fatal error during image uploads: {str(e)}"
                st.error(error_msg)
                log_message(error_msg)
            finally:
                try:
                    driver.quit()
                except:
                    pass
            st.stop()

        else:
            # CRITICAL FIX: For redirect fix task, we need to handle total_count differently
            if task_type == "Fix Redirects Status Code":
                # For redirect fix, we don't have a fixed number from df
                # We'll calculate total_count based on actual processed redirects
                total_rows = 0  # Will be updated during processing
                total_count = 0  # Will be updated during processing
            else:
                total_rows = len(df)
                total_count = total_rows
                
            if use_epochs:
                if 'current_epoch_idx' not in st.session_state:
                    st.session_state.current_epoch_idx = 0
                epochs = [df[i:i+EPOCH_SIZE] for i in range(0, total_rows, EPOCH_SIZE)]
                total_epochs = len(epochs)
                epoch_progress_increment = 100 / total_epochs if total_epochs > 0 else 0
                current_progress = [0]  # Use list to allow modification
                
                # Create placeholder for OTP container
                otp_container = st.empty()

                for epoch_offset, epoch_df in enumerate(epochs[st.session_state.current_epoch_idx:]):
                    epoch_idx = st.session_state.current_epoch_idx + epoch_offset
                    epoch_msg = f"Starting Epoch {epoch_idx + 1}/{total_epochs} with {len(epoch_df)} rows"
                    st.info(epoch_msg)
                    log_message(epoch_msg)
                    
                    if show_nestle_mena and epoch_idx == 0:
                        mena_msg = "⌛ Please complete the login of shield manually in the browser window..."
                        st.info(mena_msg)
                        log_message(mena_msg)

                    progress_text.text(f"Progress: {int(current_progress[0])}% (Epoch {epoch_idx + 1}/{total_epochs})")
                    
                    # OTP handling for Nestlé MENA starting from epoch 2
                    epoch_otp = otp_code
                    if show_nestle_mena and epoch_idx >= 1:
                        if epoch_idx not in st.session_state.otp_submitted or not st.session_state.otp_submitted[epoch_idx]:
                            with otp_container.container():
                                st.info(f"⌛ Please enter OTP for epoch {epoch_idx + 1}")
                                col1, col2 = st.columns([4, 1])
                                with col1:   
                                    otp_input = st.text_input(
                                        "OTP", 
                                        placeholder="Make sure the expiration > 25 seconds.",
                                        max_chars=6,
                                        key=f"otp_input_{epoch_idx}",
                                    )

                                with col2:
                                    submit_otp = st.button("Submit", key=f"otp_submit_{epoch_idx}")
                                    if submit_otp:
                                        if otp_input:
                                            if not otp_input.isdigit() or len(otp_input) != 6:
                                                st.error("❌ OTP must be exactly 6 digits (0-9)!")
                                            else:   
                                                st.session_state.otp_values[epoch_idx] = otp_input
                                                st.session_state.otp_submitted[epoch_idx] = True
                                        
                                        else:
                                            st.error("Please enter the OTP code!")
                        else:
                            epoch_otp = st.session_state.otp_values[epoch_idx]
                            
                    driver = initialize_driver()
                    wait = WebDriverWait(driver, LONG_WAIT)

                    try:
                        # For Nestlé MENA after first epoch
                        if show_nestle_mena and epoch_idx >= 1 and submit_otp and otp_input and (otp_input.isdigit() or len(otp_input) == 6): 
                            
    
                            login_url = f"{base_url}/user/login"
                            driver.get(login_url)
                            perform_login(
                                driver, 
                                wait, 
                                website_name, 
                                website_lang, 
                                username, 
                                password, 
                                epoch_otp,  # Use the OTP entered by user
                                False,  # Don't show Shield fields since we're doing it manually
                                "",  # Empty Shield username
                                "",  # Empty Shield password  
                                show_nestle_mena, 
                                show_nestle_family, 
                                otp
                            )
                        else:
                            # Normal login flow for first epoch or other websites
                            perform_login(
                                driver, 
                                wait, 
                                website_name, 
                                website_lang, 
                                username, 
                                password, 
                                epoch_otp,
                                show_shield, 
                                shield_username,
                                shield_password,
                                show_nestle_mena, 
                                show_nestle_family, 
                                otp
                            )
                        # Process the rows for this epoch
                        epoch_rows = len(epoch_df)
                        progress_increment = epoch_progress_increment / epoch_rows if epoch_rows > 0 else 0
                        process_rows(
                            driver, 
                            wait, 
                            epoch_df, 
                            base_url, 
                            website_name, 
                            website_lang, 
                            task_type, 
                            show_no_lang, 
                            total_rows, 
                            progress_bar, 
                            status_text, 
                            progress_text, 
                            progress_increment, 
                            current_progress, 
                            all_operation_times, 
                            total_success_count, 
                            all_failures, 
                            processed_rows, 
                            epoch_idx, 
                            total_epochs, 
                            use_epochs
                        )
                    except Exception as e:
                        error_msg = f"❌ Epoch {epoch_idx + 1} failed!"
                        st.error(error_msg)
                        log_message(error_msg)
                    finally:
                        try:
                            driver.quit()
                        except:
                            pass
                    
                    epoch_complete_msg = f"Completed Epoch {epoch_idx + 1}/{total_epochs}"
                    st.info(epoch_complete_msg)
                    log_message(epoch_complete_msg)
                    
                    current_progress[0] = min(current_progress[0] + epoch_progress_increment, 100)
                    progress_bar.progress(int(current_progress[0]))
                    progress_text.text(f"Progress: {int(current_progress[0])}% (Epoch {epoch_idx + 1}/{total_epochs})")
                    st.session_state.current_epoch_idx = epoch_idx + 1
                
                progress_text.text("Progress: 100%")
                progress_bar.progress(100)
            else:
                driver = initialize_driver()
                wait = WebDriverWait(driver, LONG_WAIT)
                try:
                    perform_login(driver, wait, website_name, website_lang, username, password, otp_code, show_shield, shield_username, shield_password, show_nestle_mena, show_nestle_family, otp)
                    if task_type == "Fix Redirects Status Code":
                        progress_increment = 100  # For redirect fix, we handle progress differently
                    else:
                        progress_increment = 100 / total_rows if total_rows > 0 else 0
                    current_progress = [0]  # Use list to allow modification
                    process_rows(driver, wait, df, base_url, website_name, website_lang, task_type, show_no_lang, total_rows, progress_bar, status_text, progress_text, progress_increment, current_progress, all_operation_times, total_success_count, all_failures, processed_rows, 0, 0, use_epochs)
                except Exception as e:
                    error_msg = f"❌ Automation has been stopped due to fetal error!"
                    st.error(error_msg)
                    log_message(error_msg)

                finally:
                    try:
                        driver.quit()
                    except:
                        pass
                progress_text.text("Progress: 100%")
                progress_bar.progress(100)

        # Calculate summary statistics
        # CRITICAL FIX: For redirect fix task, calculate total_count based on actual processed items
        if task_type == "Fix Redirects Status Code":
            # For redirect fix, total_count is the sum of success + failures
            total_count = total_success_count[0] + len(all_failures)
        else:
            total_count = len(df) if df is not None else 0
        
        total_time = time.time() - total_start_time
        avg_time = sum(all_operation_times) / len(all_operation_times) if all_operation_times else 0
        
        # Prevent division by zero
        if total_count > 0:
            success_percentage = int(total_success_count[0] / total_count * 100)
            failure_percentage = int(len(all_failures) / total_count * 100)
            incomplete_count = max(0, total_count - (total_success_count[0] + len(all_failures)))  # Prevent negative values
            incomplete_percentage = int(incomplete_count / total_count * 100)
        else:
            success_percentage = 0
            failure_percentage = 0
            incomplete_count = 0
            incomplete_percentage = 0



        # Build the summary message
        summary_message = (
            f"**📦 End of automation process!** **Stopping the application.**<br>"
            f"**Total automation execution time:** {format_time(total_time)}<br>"
            f"**Average automation time per operation:** {format_time(avg_time)}<br>"
            f"**Total:** {total_count}<br>"
            f"**Success:** {total_success_count[0]} ({success_percentage}%)<br>"
            f"**Failed:** {len(all_failures)} ({failure_percentage}%)<br>"
            f"**Incomplete:** {incomplete_count} ({incomplete_percentage}%)<br>"
        )

        # Display the summary
        st.markdown(summary_message, unsafe_allow_html=True)

        # Save automation logs
        log_file_path = save_automation_log(website_name, website_lang, summary_message, automation_logs)
        if log_file_path:
            st.info(f"📄 Automation log saved to: {log_file_path}")

        # Handle failure and incomplete reports
        incomplete_rows = []
        if task_type == "Upload images with alt text":
            for i, image_path in enumerate(image_paths):
                if i not in processed_rows:
                    incomplete_rows.append({'Image Path': os.path.basename(image_path)})
        elif task_type == "Fix Redirects Status Code":
            # For redirect fix, incomplete items are already tracked in failures
            pass
        else:
            for index, row in df.iterrows():
                if index not in processed_rows:
                    incomplete_rows.append(row.to_dict())

        if len(all_failures) > 0 or len(incomplete_rows) > 0:
            fail_df = pd.DataFrame(all_failures)
            incomplete_df = pd.DataFrame(incomplete_rows)
            
            for df_item in [fail_df, incomplete_df]:
                if 'error' in df_item.columns:
                    df_item.drop('error', axis=1, inplace=True)
                if 'screenshot' in df_item.columns:
                    df_item.drop('screenshot', axis=1, inplace=True)
                if 'Status' in df_item.columns:
                    df_item.drop('Status', axis=1, inplace=True)
                if 'Sr no' in df_item.columns:
                    df_item.drop('Sr no', axis=1, inplace=True)   
            
            combined_df = pd.concat([fail_df, incomplete_df], ignore_index=True)
            
            if 'URL' in combined_df.columns:
                combined_df = combined_df.drop_duplicates(subset=['URL'], keep='first')
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                combined_df.to_excel(writer, index=False, sheet_name='Failures Report')
            
            output.seek(0)
            
            # Create the file path for the failure report
            failure_report_filename = f"{get_website_name(website_name)}_{website_lang}_Failures_Report.xlsx"
            
            st.success("Failure report generated successfully!")
            
            st.download_button(
                label="Download Failures Report",
                data=output,
                file_name=failure_report_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No failures or incomplete items. No report generated.")

        st.stop()

    except Exception as e:
        error_msg = f"❌ Automation has been stopped due to fetal error!"
        st.error(error_msg)
        log_message(error_msg)
        
        progress_bar.progress(100)
        progress_text.text("Progress: 100%")
        total_time = time.time() - total_start_time
        avg_time = sum(all_operation_times) / len(all_operation_times) if all_operation_times else 0
        
        # Calculate total count based on task type
        if task_type == "Fix Redirects Status Code":
            total_count = total_success_count[0] + len(all_failures)
        else:
            total_count = len(df) if df is not None else 0
        
        if total_count > 0:
            success_percentage = int(total_success_count[0] / total_count * 100)
            failure_percentage = int(len(all_failures) / total_count * 100)
            incomplete_count = max(0, total_count - (total_success_count[0] + len(all_failures)))
            incomplete_percentage = int(incomplete_count / total_count * 100)
        else:
            success_percentage = 0
            failure_percentage = 0
            incomplete_count = 0
            incomplete_percentage = 0



        summary_message = (
            f"**📦 End of automation process!** **Stopping the application.**<br>"
            f"**Total automation execution time:** {format_time(total_time)}<br>"
            f"**Average automation time per operation:** {format_time(avg_time)}<br>"
            f"**Total:** {total_count}<br>"
            f"**Success:** {total_success_count[0]} ({success_percentage}%)<br>"
            f"**Failed:** {len(all_failures)} ({failure_percentage}%)<br>"
            f"**Incomplete:** {incomplete_count} ({incomplete_percentage}%)<br>"
        )

        st.markdown(summary_message, unsafe_allow_html=True)

        # Save automation logs
        log_file_path = save_automation_log(website_name, website_lang, summary_message, automation_logs)
        if log_file_path:
            st.info(f"📄 Automation log saved to: {log_file_path}")

        incomplete_rows = []
        if task_type == "Upload images with alt text":
            for i, image_path in enumerate(image_paths):
                if i not in processed_rows:
                    incomplete_rows.append({'Image Path': os.path.basename(image_path)})
        elif task_type == "Fix Redirects Status Code":
            # For redirect fix, incomplete items are already tracked in failures
            pass
        else:
            for index, row in df.iterrows():
                if index not in processed_rows:
                    incomplete_rows.append(row.to_dict())

        if len(all_failures) > 0 or len(incomplete_rows) > 0:
            fail_df = pd.DataFrame(all_failures)
            incomplete_df = pd.DataFrame(incomplete_rows)
            
            for df_item in [fail_df, incomplete_df]:
                if 'error' in df_item.columns:
                    df_item.drop('error', axis=1, inplace=True)
                if 'screenshot' in df_item.columns:
                    df_item.drop('screenshot', axis=1, inplace=True)
                if 'Status' in df_item.columns:
                    df_item.drop('Status', axis=1, inplace=True)
                if 'Sr no' in df_item.columns:
                    df_item.drop('Sr no', axis=1, inplace=True)  

            combined_df = pd.concat([fail_df, incomplete_df], ignore_index=True)
            
            if 'URL' in combined_df.columns:
                combined_df = combined_df.drop_duplicates(subset=['URL'], keep='first')
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                combined_df.to_excel(writer, index=False, sheet_name='Failures Report')
            
            output.seek(0)
            
            # Create the file path for the failure report
            failure_report_filename = f"{get_website_name(website_name)}_{website_lang}_Failures_Report.xlsx"
            
            st.success("Failure report generated successfully!")
            
            st.download_button(
                label="Download Failures Report",
                data=output,
                file_name=failure_report_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No failures or incomplete items. No report generated.")

        st.stop()