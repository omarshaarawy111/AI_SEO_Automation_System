# Installation Guide

This guide will walk you through installing the SEO Automation Tool on your system.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux Ubuntu 18.04+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free disk space
- **Network**: Stable internet connection

### Required Software
- **Python 3.9+**: [Download Python](https://www.python.org/downloads/)
- **Google Chrome**: [Download Chrome](https://www.google.com/chrome/)
- **ChromeDriver**: [Download ChromeDriver](https://chromedriver.chromium.org/downloads)

## 🚀 Installation Methods

### Method 1: Standard Installation (Recommended)

#### Step 1: Clone Repository
```bash
git clone https://github.com/omarshaarawy111/SEO_Automation.git
cd SEO_Automation
```

#### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv seo_automation_env

# Activate virtual environment
# Windows:
seo_automation_env\Scripts\activate
# macOS/Linux:
source seo_automation_env/bin/activate
```

#### Step 3: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
python -c "import streamlit, selenium, pandas; print('✅ Installation successful')"
```

#### Step 4: ChromeDriver Setup

**Option A: Automatic Setup (Recommended)**
```bash
# The tool will attempt to auto-download ChromeDriver
# Just make sure Chrome browser is installed
```

**Option B: Manual Setup**
1. Check your Chrome version: Go to `chrome://version/`
2. Download matching ChromeDriver from [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)
3. Extract and place in your system PATH or project directory

### Method 2: Portable Installation

For environments where Python installation isn't possible:

```bash
cd portable/
# Windows
gcc -o setup.exe setup.c
setup.exe

# Linux/macOS
gcc -o setup setup.c
./setup
```

## 🧪 Verify Installation

### Test Basic Functionality
```bash
# Start the application
streamlit run src/main.py

# You should see:
# "You can now view your Streamlit app in your browser."
# "Local URL: http://localhost:8501"
```

### Browser Test
1. Open [http://localhost:8501](http://localhost:8501)
2. You should see the SEO Automation Tool interface
3. Try uploading a sample file from `data/` folder

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file in the project root:
```env
# Browser settings
HEADLESS_MODE=false
BROWSER_TIMEOUT=30

# Authentication
DEFAULT_USERNAME=your_username
DEFAULT_PASSWORD=your_password

# Logging
LOG_LEVEL=INFO
```

### Chrome Browser Options
Edit `src/config.py` for custom browser settings:
```python
BROWSER_OPTIONS = {
    'headless': False,
    'window_size': '1920,1080',
    'disable_images': False,
    'user_agent': 'SEO-Automation/1.0'
}
```

## 🐛 Troubleshooting Installation

### Common Issues

#### Python Version Issues
```bash
# Check Python version
python --version
# Should show 3.9 or higher

# If using older version
# Install Python 3.9+ from python.org
```

#### ChromeDriver Issues
```bash
# Check Chrome version
google-chrome --version  # Linux
chrome --version         # macOS
# Check in chrome://version/ for Windows

# Download matching ChromeDriver version
# Place in PATH or project directory
```

#### Permission Issues (macOS/Linux)
```bash
# Make ChromeDriver executable
chmod +x chromedriver

# If security warning on macOS
xattr -d com.apple.quarantine chromedriver
```

#### Virtual Environment Issues
```bash
# If virtual environment fails
pip install virtualenv
virtualenv seo_automation_env

# Or use conda
conda create -n seo_automation python=3.9
conda activate seo_automation
```

### Dependencies Issues

#### Selenium WebDriver Issues
```bash
# Reinstall selenium
pip uninstall selenium
pip install selenium==4.15.0
```

#### Streamlit Issues
```bash
# Clear Streamlit cache
streamlit cache clear

# Reinstall Streamlit
pip uninstall streamlit
pip install streamlit==1.28.0
```

## 🔄 Updating

### Update Application
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
streamlit run src/main.py
```

### Update ChromeDriver
```bash
# Check Chrome version
chrome --version

# Download matching ChromeDriver
# Replace existing ChromeDriver file
```

## 🗂️ Directory Structure After Installation

```
SEO_Automation/
├── src/                    # Main application code
├── data/                   # Sample data files
├── docs/                   # Documentation (you're here!)
├── portable/               # Portable app files
├── seo_automation_env/     # Virtual environment
├── requirements.txt        # Python dependencies
└── README.md              # Project overview
```

## 🧹 Uninstallation

### Remove Virtual Environment
```bash
# Deactivate environment
deactivate

# Remove environment folder
rm -rf seo_automation_env  # Linux/macOS
rmdir /s seo_automation_env  # Windows
```

### Remove Project
```bash
# Remove entire project
cd ..
rm -rf SEO_Automation
```

## 🆘 Need Help?

If you encounter issues during installation:

1. **Check Requirements**: Ensure all prerequisites are met
2. **Review Error Messages**: Most errors are self-explanatory
3. **Check Logs**: Look for error details in terminal output
4. **GitHub Issues**: [Report installation issues](https://github.com/omarshaarawy111/SEO_Automation/issues)

## ✅ Installation Complete!

Once installation is successful:
- 📖 **Next**: Read the [User Guide](user-guide.md)
- 📊 **Prepare Data**: Check [Data Formats](data-formats.md)
- 🚀 **Start Automating**: Launch the tool with `streamlit run src/main.py`

---

**Installation completed successfully?** Continue to the [User Guide](user-guide.md) to start using the tool!