# Troubleshooting Guide

Complete troubleshooting guide for common issues with the SEO Automation Tool.

## 🔍 Quick Diagnosis

### Before You Start
1. **Check System Requirements**: Ensure Python 3.9+, Chrome browser, and ChromeDriver are installed
2. **Verify Installation**: Run `python -c "import streamlit, selenium, pandas; print('✅ OK')"`
3. **Test Basic Functionality**: Can you access [http://localhost:8501](http://localhost:8501)?
4. **Review Error Messages**: Most issues have self-explanatory error messages

## 🚨 Installation Issues

### Python Version Problems

**Issue**: `python: command not found` or version conflicts
```bash
python --version  # Shows wrong version or command not found
```

**Solutions**:
```bash
# Install Python 3.9+ from python.org
# Then verify:
python3 --version
python3 -m pip --version

# Use python3 instead of python:
python3 -m venv seo_automation_env
python3 -m pip install -r requirements.txt
```

**Alternative**: Use Anaconda/Miniconda:
```bash
conda create -n seo_automation python=3.9
conda activate seo_automation
pip install -r requirements.txt
```

### Virtual Environment Issues

**Issue**: Virtual environment creation fails
```bash
# Error examples:
# "No module named venv"
# "Access denied"
# "Permission error"
```

**Solutions**:
```bash
# Method 1: Use virtualenv
pip install virtualenv
virtualenv seo_automation_env

# Method 2: Use conda
conda create -n seo_automation python=3.9

# Method 3: System-wide installation (not recommended)
pip install -r requirements.txt --user
```

### Dependency Installation Problems

**Issue**: `pip install -r requirements.txt` fails

**Common Errors and Solutions**:

**Error**: `Microsoft Visual C++ 14.0 is required` (Windows)
```bash
# Install Microsoft C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

**Error**: `Failed building wheel for [package]`
```bash
# Upgrade pip and try again
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Error**: `Permission denied`
```bash
# Use --user flag
pip install -r requirements.txt --user

# Or fix permissions (Linux/macOS)
sudo chown -R $USER:$USER ~/.local
```

## 🌐 Browser and ChromeDriver Issues

### ChromeDriver Version Mismatch

**Issue**: `SessionNotCreatedException: session not created: This version of ChromeDriver only supports Chrome version X`

**Solution**: Match ChromeDriver version to Chrome browser
```bash
# Check Chrome version
google-chrome --version  # Linux
chrome --version         # macOS
# Windows: chrome://version/ in browser

# Download matching ChromeDriver from:
# https://chromedriver.chromium.org/downloads

# Place ChromeDriver in:
# - Project directory: SEO_Automation/chromedriver
# - System PATH: /usr/local/bin/ (macOS/Linux) or C:\Windows\System32\ (Windows)
```

**Auto-fix Script** (Linux/macOS):
```bash
#!/bin/bash
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%.*}")
wget -O chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip chromedriver.zip
chmod +x chromedriver
```

### ChromeDriver Not Found

**Issue**: `WebDriverException: 'chromedriver' executable needs to be in PATH`

**Solutions**:

**Option 1**: Add to PATH
```bash
# Linux/macOS
export PATH=$PATH:/path/to/chromedriver
echo 'export PATH=$PATH:/path/to/chromedriver' >> ~/.bashrc

# Windows
# Add chromedriver folder to System PATH via Environment Variables
```

**Option 2**: Specify ChromeDriver location in code
```python
# Edit src/browser_utils.py
service = Service('/full/path/to/chromedriver')
driver = webdriver.Chrome(service=service, options=options)
```

### Chrome Browser Issues

**Issue**: Chrome crashes or doesn't start

**Solutions**:
```bash
# Kill existing Chrome processes
pkill chrome  # Linux/macOS
taskkill /f /im chrome.exe  # Windows

# Clear Chrome user data
rm -rf ~/.config/google-chrome/Default  # Linux
rm -rf ~/Library/Application\ Support/Google/Chrome/Default  # macOS
# Windows: Delete C:\Users\%USERNAME%\AppData\Local\Google\Chrome\User Data\Default

# Restart Chrome and try again
```

## 🔐 Authentication Issues

### Login Failures

**Issue**: Authentication fails despite correct credentials

**Diagnostic Steps**:
1. **Manual Test**: Can you log in manually using the same browser?
2. **CAPTCHA Check**: Is there a CAPTCHA preventing automated login?
3. **Two-Factor Auth**: Does your account require 2FA/OTP?
4. **Rate Limiting**: Are you being blocked for too many attempts?

**Solutions**:
```python
# Increase timeout in src/config.py
AUTH_CONFIG = {
    'login_timeout': 60,  # Increase from 30
    'max_login_attempts': 5,  # Increase attempts
    'retry_delay': 10  # Wait longer between retries
}
```

### Two-Factor Authentication (2FA/OTP) Issues

**Issue**: OTP/2FA challenges not handled properly

**Solutions**:
1. **Manual OTP Entry**: Tool should pause for manual OTP input
2. **Extended Timeout**: Increase OTP wait time in config
3. **Backup Codes**: Use backup authentication codes if available

**Configuration**:
```python
# In src/config.py
AUTH_CONFIG = {
    'otp_wait_time': 120,  # 2 minutes for OTP entry
    'otp_max_attempts': 3
}
```

### Session Timeout Issues

**Issue**: Session expires during long operations

**Solutions**:
```python
# Increase session timeout
AUTH_CONFIG = {
    'session_timeout': 7200,  # 2 hours
    'session_refresh_interval': 1800  # Refresh every 30 minutes
}

# Add session keep-alive mechanism
def keep_session_alive(driver):
    driver.refresh()
    time.sleep(2)
```

## 📁 File Processing Issues

### Excel/CSV File Problems

**Issue**: File upload fails or data not recognized

**Common Problems and Solutions**:

**Problem**: File format not supported
```
Error: "File format not recognized"
```
**Solution**:
- Use Excel 2007+ (.xlsx) format
- For CSV: Save as UTF-8 encoding
- Avoid special characters in filenames

**Problem**: Column headers don't match
```
Error: "Required column 'URL' not found"
```
**Solution**:
- Use exact column names: `URL`, `Meta Title`, `Meta Description`
- Check for extra spaces or special characters
- Use provided templates from `data/` folder

**Problem**: Data validation fails
```
Error: "Invalid URL format in row 3"
```
**Solution**:
```python
# Validate your data before upload:
import pandas as pd

df = pd.read_excel('your_file.xlsx')
print(df.columns.tolist())  # Check column names
print(df.head())  # Check first few rows
print(df.isnull().sum())  # Check for empty values
```

### Large File Handling

**Issue**: Processing large files (1000+ URLs) causes memory issues

**Solutions**:
1. **Batch Processing**: Split large files into smaller chunks
```python
# Split large Excel files
import pandas as pd

df = pd.read_excel('large_file.xlsx')
chunk_size = 100

for i in range(0, len(df), chunk_size):
    chunk = df[i:i+chunk_size]
    chunk.to_excel(f'batch_{i//chunk_size + 1}.xlsx', index=False)
```

2. **Memory Optimization**: Process in smaller batches
```python
# In src/config.py
OPERATION_CONFIG = {
    'batch_size': 50,  # Reduce from default
    'memory_limit_mb': 512
}
```

## 🌐 Website-Specific Issues

### Element Not Found Errors

**Issue**: `NoSuchElementException: Unable to locate element`

**Causes**:
- Website structure changed
- Elements load dynamically (JavaScript)
- Different page layouts
- A/B testing variations

**Solutions**:
1. **Update Selectors**: Modify element selectors in code
```python
# In src/metatags_utils.py, update selectors:
TITLE_SELECTORS = [
    'input[name="title"]',
    'input[id="page-title"]',
    'textarea[name="meta_title"]',
    # Add more variations
]
```

2. **Increase Wait Times**:
```python
# In src/config.py
BROWSER_CONFIG = {
    'implicit_wait': 20,  # Increase from 10
    'explicit_wait': 30
}
```

3. **Add Debug Screenshots**:
```python
# Add to your automation code
driver.save_screenshot(f'debug_screenshot_{timestamp}.png')
```

### JavaScript-Heavy Websites

**Issue**: Content loads via JavaScript, elements not immediately available

**Solutions**:
```python
# Use explicit waits for dynamic content
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 30)
element = wait.until(EC.presence_of_element_located((By.ID, "dynamic-element")))
```

### Rate Limiting and Blocking

**Issue**: Website blocks automated requests

**Signs**:
- 429 (Too Many Requests) errors
- CAPTCHA challenges
- IP blocking
- "Unusual activity" warnings

**Solutions**:
1. **Add Delays**:
```python
# In src/config.py
OPERATION_CONFIG = {
    'delay_between_requests': 3,  # 3 seconds between operations
    'random_delay_range': (2, 5)  # Random delay 2-5 seconds
}
```

2. **Human-like Behavior**:
```python
# Add random mouse movements and scrolling
from selenium.webdriver.common.action_chains import ActionChains
import random

def human_like_delay():
    time.sleep(random.uniform(1, 3))
    
def random_scroll(driver):
    driver.execute_script(f"window.scrollBy(0, {random.randint(100, 300)});")
```

## ⚡ Performance Issues

### Slow Processing Speed

**Issue**: Automation runs very slowly

**Optimization Steps**:

1. **Browser Optimization**:
```python
# In src/browser_utils.py, add Chrome options:
chrome_options.add_argument('--disable-images')
chrome_options.add_argument('--disable-javascript')  # If not needed
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
```

2. **Concurrent Processing** (Advanced):
```python
# Process multiple URLs simultaneously (use carefully)
import concurrent.futures

def process_batch(urls_batch):
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = executor.map(process_single_url, urls_batch)
    return list(results)
```

3. **System Optimization**:
- Close unnecessary applications
- Use SSD storage for better I/O
- Increase available RAM
- Use wired internet connection

### Memory Issues

**Issue**: High memory usage or out-of-memory errors

**Solutions**:
1. **Browser Memory Management**:
```python
# Restart browser every N operations
def restart_browser_if_needed(operation_count):
    if operation_count % 100 == 0:  # Every 100 operations
        driver.quit()
        driver = initialize_new_driver()
    return driver
```

2. **Data Processing Optimization**:
```python
# Process data in chunks instead of loading everything
def process_large_file(filename, chunk_size=100):
    for chunk in pd.read_excel(filename, chunksize=chunk_size):
        process_chunk(chunk)
        del chunk  # Free memory
```

## 📊 Logging and Debugging

### Enable Debug Logging

**Add detailed logging** to diagnose issues:

```python
# In src/config.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
```

### Common Log Messages

**Understanding error messages**:

```
[ERROR] Element not found: input[name="title"]
→ Solution: Check if page structure changed

[WARNING] Slow page load: 30+ seconds
→ Solution: Check internet connection or increase timeout

[ERROR] Authentication failed: Invalid credentials
→ Solution: Verify username/password manually

[INFO] Retrying operation (attempt 2/3)
→ Normal: Tool is handling temporary errors automatically
```

### Debug Mode

**Enable debug mode** for detailed troubleshooting:

```python
# In src/main.py, add debug flag
DEBUG_MODE = True

if DEBUG_MODE:
    # Take screenshots before/after each operation
    driver.save_screenshot(f'before_operation_{timestamp}.png')
    
    # Log HTML source for problematic pages
    with open(f'page_source_{timestamp}.html', 'w') as f:
        f.write(driver.page_source)
```

## 🆘 Getting Help

### Self-Diagnosis Checklist

Before asking for help, check:
- [ ] Python version is 3.9+
- [ ] Virtual environment is activated
- [ ] All dependencies installed correctly
- [ ] ChromeDriver matches Chrome version
- [ ] Internet connection is stable
- [ ] Login credentials work manually
- [ ] File format follows templates
- [ ] No antivirus blocking browser automation

### Error Reporting

**When reporting issues**, include:

1. **System Information**:
```bash
python --version
pip freeze > installed_packages.txt
uname -a  # Linux/macOS
systeminfo  # Windows
```

2. **Error Details**:
- Full error message and traceback
- Steps to reproduce the issue
- Sample data file (if applicable)
- Screenshots of the problem

3. **Log Files**:
- Application logs (`logs/automation.log`)
- Browser console errors (F12 → Console)
- Network errors (F12 → Network)

### Support Channels

1. **GitHub Issues**: [Report bugs](https://github.com/omarshaarawy111/SEO_Automation/issues)
2. **GitHub Discussions**: [Ask questions](https://github.com/omarshaarawy111/SEO_Automation/discussions)
3. **Documentation**: Check other docs sections first

### Create Minimal Reproduction

**For complex issues**, create a minimal example:
```python
# minimal_test.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def test_basic_functionality():
    try:
        service = Service('./chromedriver')
        driver = webdriver.Chrome(service=service)
        driver.get('https://www.google.com')
        print("✅ Basic browser automation works")
        driver.quit()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_basic_functionality()
```

## 🔄 Regular Maintenance

### Prevent Issues Before They Happen

**Monthly Checks**:
- Update Chrome browser
- Update ChromeDriver
- Update Python packages: `pip install -r requirements.txt --upgrade`
- Clear browser cache and cookies
- Check for new ChromeDriver compatibility

**Weekly Checks**:
- Monitor log file sizes
- Clean up screenshot/debug files
- Test with small sample data
- Verify website structure hasn't changed

---

**Still having issues?** Don't worry! Most problems have solutions. Check the [GitHub Issues](https://github.com/omarshaarawy111/SEO_Automation/issues) or create a new issue with detailed information about your problem.