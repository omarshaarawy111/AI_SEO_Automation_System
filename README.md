# 🚀 SEO Automation App

## 📖 Complete Documentation Available!

**🚀 [View Professional Documentation →](docs/README.md)**

This repository now includes comprehensive documentation covering:
- Complete installation guide
- Detailed user manual  
- API reference
- Troubleshooting guide
- Best practices

---

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)
![Selenium](https://img.shields.io/badge/Selenium-Automation-brightgreen?logo=selenium)

A **Streamlit + Selenium** automation tool designed to simplify bulk **SEO workflows**.  
Easily update **meta tags, URLs, redirects, and images** across multilingual websites.

---

## ✨ Features

- 📑 **Bulk Processing**: Excel/CSV input for metadata and images  
- 📝 **SEO Tasks Supported**:
  - Add/Edit H1  
  - Update Meta Titles
  - Update Meta Descriptions
  - Update Both Titles & Descriptions
  - Modify URL Aliases
  - Create URL Redirects
  - Upload Images with Alt Text
- 🌍 **Multi-language Support**: Works with English, Arabic, French (extensible)  
- 📊 **Progress Tracking**: Real-time progress bar + status log  
- 📂 **Error Reporting**: Auto-generated Excel report for failed updates  
- 🖥️ **Sleep Prevention**: Keeps your system awake during automation  

---

## 📂 Project Structure

```
seo_automation_app/
│
├── archive/             # Old versions / backup scripts
├──assets/               # Images, lottie file etc...
│   ├── icon.ico
│   ├── sample.jpg
│   └── Website SEO Audit.json
│   
│ 
│ 
├── src/                  # Main application source
│   ├── main.py           # 🚀 Entry point for Streamlit app
│   ├── auth.py           # Authentication handling
│   ├── config.py         # Configurations
│   ├── browser_utils.py  # Selenium helpers
│   ├── metatags_utils.py # Meta updates
│   ├── file_utils.py     # File parsing
│   └── components/       # UI components (sidebar, footer, screen, etc.)
│       ├── screen.py
│       └── footer.py
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

```bash
# 1. Clone repository
git clone https://github.com/omarshaarawy111/AI_SEO_Automation_System.git
cd AI_SEO_Automation_System

# 2. Create virtual environment (recommended)
python -m venv venv
# Activate it
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Streamlit app
streamlit run src/main.py
```

> ⚠️ **Note**: Ensure you have **Google Chrome** + **ChromeDriver** installed and accessible in your PATH.  
Download here: [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)

---

## ▶️ Usage

1. Start the app:  
   ```bash
   streamlit run src/main.py
   ```
2. In the web UI:
   - Upload **Excel/CSV** (for titles, descriptions, URLs) or **Images** (for uploads).  
   - Choose **task type** (meta tags, redirects, images, etc.).  
   - Enter **credentials** (username, password, OTP if required).  
   - Click **Automate** 🚀.  
3. Watch the progress bar and logs.  
4. If failures occur → download the generated **error report** (Excel).  

---

## 📋 Input File Requirements

### For Meta Updates
Excel/CSV must include:
```
URL | Meta Title | Meta Description
```

### For URL Alias / Redirects
```
Old URL | New URL Structure | Redirect Type
```

### For Image Uploads
```
Image Name | Alt Text | Target URL
```

---

## 📦 Requirements

- `python 3.9+`
- `streamlit`
- `selenium`
- `pandas`
- `openpyxl`
- `xlsxwriter`

(see [requirements.txt](./requirements.txt) for full list)

---


