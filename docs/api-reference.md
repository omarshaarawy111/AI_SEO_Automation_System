# API Reference

Technical documentation for developers working with the SEO Automation Tool codebase.

## 🏗️ Architecture Overview

```
SEO Automation Tool
├── src/main.py              # Streamlit application entry point
├── src/auth.py              # Authentication handling
├── src/config.py            # Configuration management
├── src/browser_utils.py     # Selenium WebDriver utilities
├── src/metatags_utils.py    # Meta tag manipulation
├── src/login_utils.py       # Login flow management
├── src/file_utils.py        # File processing utilities
├── src/image_utils.py       # Image upload operations
└── src/components/          # UI components
    ├── screen.py            # Screen management
    └── footer.py            # Footer component
```

## 📦 Core Modules

### `main.py` - Application Entry Point

Main Streamlit application orchestrating all components.

```python
def main():
    """Main application entry point"""
    
def setup_page_config():
    """Configure Streamlit page settings"""
    
def initialize_session_state():
    """Initialize session variables"""
    
def render_ui():
    """Render main user interface"""
```

**Key Functions**:
- Application initialization
- UI rendering coordination
- Session state management
- Error handling and logging

### `auth.py` - Authentication Management

Handles user authentication and session management.

```python
class AuthManager:
    """Manages authentication workflows"""
    
    def __init__(self, config: dict):
        """Initialize authentication manager"""
        
    def login(self, username: str, password: str) -> bool:
        """Perform login operation"""
        
    def handle_otp(self, otp_code: str) -> bool:
        """Handle two-factor authentication"""
        
    def is_authenticated(self) -> bool:
        """Check authentication status"""
        
    def logout(self):
        """Perform logout operation"""
```

**Methods**:
- `login(username, password)` - Standard login
- `handle_otp(otp_code)` - Two-factor authentication
- `is_authenticated()` - Session validation
- `logout()` - Session termination

### `config.py` - Configuration Management

Central configuration management for the application.

```python
# Browser Configuration
BROWSER_CONFIG = {
    'headless': False,
    'window_size': '1920,1080',
    'implicit_wait': 10,
    'page_load_timeout': 30,
    'user_agent': 'SEO-Automation/1.0'
}

# Authentication Settings
AUTH_CONFIG = {
    'login_timeout': 30,
    'otp_wait_time': 60,
    'max_login_attempts': 3,
    'session_timeout': 3600
}

# Operation Settings
OPERATION_CONFIG = {
    'max_retries': 3,
    'retry_delay': 5,
    'batch_size': 50,
    'concurrent_operations': 1
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file': 'logs/automation.log'
}
```

**Configuration Sections**:
- **Browser Settings**: WebDriver options
- **Authentication**: Login and session parameters
- **Operations**: Retry logic and batch processing
- **Logging**: Log levels and output formats

### `browser_utils.py` - Selenium WebDriver Utilities

Browser automation utilities and WebDriver management.

```python
class BrowserManager:
    """Manages browser automation operations"""
    
    def __init__(self, config: dict):
        """Initialize browser manager with configuration"""
        
    def initialize_driver(self, headless: bool = False) -> webdriver.Chrome:
        """Initialize ChromeDriver with options"""
        
    def safe_click(self, element: WebElement) -> bool:
        """Safely click element with error handling"""
        
    def safe_send_keys(self, element: WebElement, text: str) -> bool:
        """Safely send keys to element"""
        
    def wait_for_element(self, locator: tuple, timeout: int = 10) -> WebElement:
        """Wait for element presence with timeout"""
        
    def take_screenshot(self, filename: str):
        """Capture screenshot for debugging"""
        
    def close_driver(self):
        """Safely close browser and cleanup"""
```

**Key Methods**:
- `initialize_driver()` - WebDriver setup
- `safe_click()` - Element interaction with error handling
- `wait_for_element()` - Explicit wait implementation
- `take_screenshot()` - Debug screenshot capture

**Usage Example**:
```python
from src.browser_utils import BrowserManager

browser = BrowserManager(config)
driver = browser.initialize_driver()
element = browser.wait_for_element(("id", "submit-button"))
browser.safe_click(element)
```

### `metatags_utils.py` - Meta Tag Operations

Handles meta tag detection, extraction, and modification.

```python
class MetaTagManager:
    """Manages meta tag operations"""
    
    def __init__(self, driver: webdriver.Chrome):
        """Initialize with WebDriver instance"""
        
    def get_meta_title(self) -> str:
        """Extract current page title"""
        
    def get_meta_description(self) -> str:
        """Extract current meta description"""
        
    def update_meta_title(self, new_title: str) -> bool:
        """Update page meta title"""
        
    def update_meta_description(self, new_description: str) -> bool:
        """Update page meta description"""
        
    def validate_meta_changes(self, expected_title: str = None, 
                            expected_description: str = None) -> dict:
        """Verify meta tag updates"""
        
    def get_all_meta_tags(self) -> dict:
        """Extract all meta tags from page"""
```

**SEO Validation Rules**:
```python
META_VALIDATION_RULES = {
    'title': {
        'min_length': 10,
        'max_length': 60,
        'required': True
    },
    'description': {
        'min_length': 120,
        'max_length': 160,
        'required': True
    }
}
```

### `login_utils.py` - Login Flow Management

Manages authentication workflows and login procedures.

```python
class LoginManager:
    """Handles login workflows"""
    
    def __init__(self, driver: webdriver.Chrome, config: dict):
        """Initialize login manager"""
        
    def detect_login_form(self) -> dict:
        """Detect login form elements"""
        
    def perform_login(self, username: str, password: str) -> bool:
        """Execute login procedure"""
        
    def handle_otp_challenge(self) -> bool:
        """Handle OTP/2FA challenges"""
        
    def verify_login_success(self) -> bool:
        """Verify successful authentication"""
        
    def handle_login_failure(self, error: Exception):
        """Handle and log login failures"""
```

**Login Flow**:
1. Navigate to login page
2. Detect form elements
3. Input credentials
4. Handle 2FA if required
5. Verify success
6. Handle failures and retries

### `file_utils.py` - File Processing Utilities

Handles file parsing, validation, and data processing.

```python
class FileManager:
    """Manages file operations and data processing"""