# Netrun Systems Website Deployment

This is a Flask-based website for Netrun Systems, showcasing the company's cross-tenant Azure governance solutions.

## Requirements

- Python 3.12
- Flask

## Installation

1. Install the required packages:
```
pip install flask
```

2. Run the application:
```
python app.py
```

## Deployment to Azure

This website is configured for deployment to Azure App Service with Python 3.12 runtime.

### Deployment Options

1. **Zip Deploy** (Recommended)
   - Upload the zip package to Azure App Service
   - Azure will automatically detect the Python application and deploy it

2. **FTP Deploy**
   - Upload the files via FTP to the Azure App Service
   - FTP credentials are in the PublishSettings file

3. **GitHub Integration**
   - Connect your GitHub repository to Azure App Service
   - Set up continuous deployment

## File Structure

- `/src` - Main application directory
  - `app.py` - Flask application entry point
  - `/static` - Static assets
    - `/css` - Stylesheets
    - `/images` - Images and logos
    - `/js` - JavaScript files
  - `/templates` - HTML templates

## Contact

For any questions or support, please contact:
- Email: daniel@netrunsystems.com
- Phone: (805) 707-4828
