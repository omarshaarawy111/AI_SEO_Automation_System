# User Guide

Complete guide to using the SEO Automation Tool for all your SEO workflow needs.

## 🎯 Overview

The SEO Automation Tool streamlines bulk SEO operations through an intuitive web interface. You can update meta tags, manage URLs, upload images, and track progress in real-time.

## 🚀 Getting Started

### Launch the Application
```bash
# Navigate to project directory
cd SEO_Automation

# Activate virtual environment
source seo_automation_env/bin/activate  # macOS/Linux
# or
seo_automation_env\Scripts\activate     # Windows

# Start the application
streamlit run src/main.py
```

The application will open at [http://localhost:8501](http://localhost:8501)

## 🖥️ User Interface Overview

### Main Dashboard Components

#### 1. **Header Section**
- Application title and version
- Status indicators
- System wake-lock status

#### 2. **File Upload Area**
- Excel/CSV file upload for data
- Image upload for bulk image operations
- File format validation
- Sample file download links

#### 3. **Task Selection Panel**
Choose your automation task:
- Update Meta Titles
- Update Meta Descriptions  
- Update Both Titles & Descriptions
- Modify URL Aliases
- Create URL Redirects
- Upload Images with Alt Text

#### 4. **Authentication Section**
- Username and password inputs
- OTP (One-Time Password) support
- Remember credentials option
- Login status indicator

#### 5. **Progress Monitor**
- Real-time progress bar
- Operation status logs
- Error counter
- Estimated time remaining

## 📊 Operations Guide

### Meta Tag Operations

#### Update Meta Titles

**What it does**: Updates the `<title>` tag on specified pages

**Steps**:
1. **Prepare Data**: Create Excel/CSV with columns: `URL`, `Meta Title`
2. **Upload File**: Click "Choose file" and select your data file
3. **Select Task**: Choose "Update Meta Titles"
4. **Enter Credentials**: Input your website login details
5. **Start Automation**: Click "🚀 Automate" button
6. **Monitor Progress**: Watch the progress bar and logs

**Example Data**:
```csv
URL,Meta Title
https://mysite.com/page1,New SEO Optimized Title
https://mysite.com/page2,Another Great Page Title
https://mysite.com/blog/post1,Blog Post SEO Title
```

#### Update Meta Descriptions

**What it does**: Updates the `<meta name="description">` tag

**Steps**: Same as Meta Titles, but use "Update Meta Descriptions" task

**Example Data**:
```csv
URL,Meta Description
https://mysite.com/page1,Compelling description under 160 characters that drives clicks
https://mysite.com/page2,Another effective meta description for better CTR
```

#### Update Both Titles & Descriptions

**What it does**: Updates both title and description tags simultaneously

**Example Data**:
```csv
URL,Meta Title,Meta Description
https://mysite.com/page1,SEO Title,Great meta description here
https://mysite.com/page2,Another Title,Another description here
```

### URL Management Operations

#### Modify URL Aliases

**What it does**: Changes the URL structure/slug of existing pages

**Steps**:
1. **Prepare Data**: Excel/CSV with `Current URL`, `New URL Structure`
2. **Upload and Process**: Follow standard workflow
3. **Verify Changes**: Check that redirects work properly

**Example Data**:
```csv
Current URL,New URL Structure
https://mysite.com/old-product-name,https://mysite.com/new-product-name
https://mysite.com/category/old-slug,https://mysite.com/category/new-slug
```

#### Create URL Redirects

**What it does**: Implements 301/302 redirects for SEO link equity preservation

**Redirect Types**:
- **301 (Permanent)**: For permanent content moves
- **302 (Temporary)**: For temporary redirects

**Example Data**:
```csv
Old URL,New URL,Redirect Type
https://mysite.com/old-page,https://mysite.com/new-page,301
https://mysite.com/temp-sale,https://mysite.com/products,302
```

### Image Operations

#### Bulk Image Upload with Alt Text

**What it does**: Uploads images to your website with SEO-optimized alt text

**Steps**:
1. **Prepare Images**: Place all images in a folder
2. **Prepare Data**: Create CSV with `Image Name`, `Alt Text`, `Target URL`
3. **Upload Both**: Upload the CSV and select the image folder
4. **Process**: Run the automation

**Example Data**:
```csv
Image Name,Alt Text,Target URL
product-hero.jpg,Premium leather handbag with gold hardware,https://mysite.com/products/handbag
team-photo.png,Professional team of marketing experts,https://mysite.com/about/team
logo-new.svg,Company logo with modern design elements,https://mysite.com/home
```

**Supported Image Formats**:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- SVG (.svg)
- GIF (.gif)

## 🔐 Authentication Guide

### Standard Login
1. **Username**: Enter your website admin username
2. **Password**: Enter your password
3. **Login**: Tool will automatically log into your website

### Two-Factor Authentication (OTP)
If your website uses 2FA:
1. Enter username and password
2. Tool will detect OTP requirement
3. **Manual Step**: Check your phone/email for OTP code
4. **Enter OTP**: Input the code when prompted
5. **Continue**: Automation proceeds after successful authentication

### Session Management
- **Auto-logout**: Tool handles session management
- **Session Timeout**: Configurable timeout settings
- **Re-authentication**: Automatic retry if session expires

## 📈 Monitoring and Progress

### Progress Tracking
- **Overall Progress**: Percentage completion bar
- **Current Operation**: Shows which URL/item is being processed
- **Success Counter**: Number of successful operations
- **Error Counter**: Number of failed operations
- **Time Estimates**: Remaining time calculation

### Real-time Logs
The log panel shows:
```
[2024-08-19 14:30:15] Starting automation for 25 URLs
[2024-08-19 14:30:16] ✅ Login successful
[2024-08-19 14:30:18] Processing: https://mysite.com/page1
[2024-08-19 14:30:20] ✅ Meta title updated successfully
[2024-08-19 14:30:22] Processing: https://mysite.com/page2
[2024-08-19 14:30:23] ❌ Error: Element not found
[2024-08-19 14:30:25] Retrying operation...
```

### Error Handling
- **Automatic Retries**: Failed operations retry automatically
- **Error Logging**: Detailed error information captured
- **Continue on Error**: Process continues despite individual failures
- **Error Reports**: Downloadable Excel report of all failures

## 📊 Results and Reporting

### Success Indicators
- ✅ **Green checkmarks**: Successful operations
- 📊 **Progress completion**: 100% when finished
- 🎉 **Success message**: Final completion notification

### Error Reports
When errors occur, the tool generates:
- **Excel Report**: Downloadable error report
- **Error Details**: Specific error messages and URLs
- **Retry Suggestions**: Recommendations for fixing issues

**Error Report Columns**:
- Failed URL
- Operation Type
- Error Message
- Timestamp
- Suggested Fix

### Performance Metrics
- **Total Operations**: Number of items processed
- **Success Rate**: Percentage of successful operations
- **Processing Speed**: Items per minute
- **Total Time**: Complete operation duration

## 🛠️ Advanced Features

### Multi-language Support
The tool supports:
- **English**: Default language
- **Arabic**: RTL text support
- **French**: Accent character handling
- **Custom Languages**: Extensible language support

### Batch Processing
- **Smart Batching**: Automatic batch size optimization
- **Memory Management**: Efficient resource usage
- **Large Datasets**: Support for thousands of URLs
- **Resume Capability**: Continue interrupted operations

### System Integration
- **Wake Lock**: Prevents computer sleep during operations
- **Background Processing**: Minimizable browser window
- **Resource Monitoring**: CPU and memory usage tracking
- **Auto-recovery**: Handles browser crashes gracefully

## ⚡ Tips for Optimal Performance

### Data Preparation
1. **Clean Data**: Remove empty rows and invalid URLs
2. **URL Testing**: Verify URLs are accessible before automation
3. **Batch Sizing**: Process 50-100 URLs at a time for best performance
4. **Content Review**: Ensure meta content follows SEO guidelines

### System Optimization
1. **Close Applications**: Free up system resources
2. **Stable Connection**: Use wired internet for reliability
3. **Browser Updates**: Keep Chrome and ChromeDriver updated
4. **System Resources**: Monitor RAM and CPU usage

### Error Prevention
1. **Backup First**: Always backup your website before bulk operations
2. **Test Small**: Run small test batches before large operations
3. **Verify Credentials**: Test login manually before automation
4. **Check Permissions**: Ensure user account has edit permissions

## 🚨 Important Notes

### Before Starting Automation
- ⚠️ **Backup your website data**
- ⚠️ **Test with 2-3 URLs first**
- ⚠️ **Verify login credentials work**
- ⚠️ **Check website availability**

### During Automation
- 🔄 **Don't close the browser window**
- 🔄 **Keep computer awake** (tool handles this)
- 🔄 **Monitor for errors**
- 🔄 **Don't use computer for other tasks**

### After Automation
- ✅ **Verify changes on your website**
- ✅ **Review error report if generated**
- ✅ **Test website functionality**
- ✅ **Monitor SEO performance**

## 🆘 Common Issues and Solutions

### Authentication Problems
**Issue**: Login fails
**Solutions**:
- Verify credentials manually in browser
- Check for CAPTCHA requirements
- Clear browser cookies
- Try incognito mode test

### File Upload Issues
**Issue**: Excel/CSV not recognized
**Solutions**:
- Use provided templates
- Save as Excel 2007+ format
- Check column headers match exactly
- Remove special characters

### Browser Issues
**Issue**: ChromeDriver errors
**Solutions**:
- Update Chrome browser
- Download matching ChromeDriver version
- Restart the application
- Check system PATH

### Performance Issues
**Issue**: Slow processing
**Solutions**:
- Reduce batch size
- Close other applications
- Check internet connection
- Monitor system resources

## 📞 Support

Need help? Here are your options:

1. **Documentation**: Check other docs sections
2. **Email the developer**: [omar.shaarawy@eg.nestle.com](mailto:omar.shaarawy@eg.nestle.com)
3. **Troubleshooting**: See [troubleshooting.md](troubleshooting.md)
4. **GitHub Issues**: [Report bugs](https://github.com/omarshaarawy111/SEO_Automation/issues)
5. **Best Practices**: Review [best-practices.md](best-practices.md)

---

**Ready to automate?** Make sure you've read the [Best Practices](best-practices.md) guide for optimal results!