# Netrun Systems Website

This is a Flask-based website for Netrun Systems, showcasing the company's cross-tenant Azure governance solutions.

## Repository Structure

- `app.py` - Flask application entry point
- `/static` - Static assets
  - `/css` - Stylesheets
  - `/images` - Images and logos
  - `/js` - JavaScript files
- `/templates` - HTML templates
- `requirements.txt` - Python dependencies
- `.github/workflows` - GitHub Actions workflow for Azure deployment

## Local Development

1. Install the required packages:
```
pip install -r requirements.txt
```

2. Run the application:
```
python app.py
```

3. Access the website at http://localhost:8000

## Deployment to Azure

This repository is configured for automatic deployment to Azure Web App using GitHub Actions.

### Setup Instructions

1. Fork or clone this repository to your GitHub account
2. In the Azure Portal, navigate to your App Service
3. Go to Deployment Center > GitHub Actions
4. Connect your GitHub repository
5. Create a new secret in your GitHub repository:
   - Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
   - Value: The contents of your PublishSettings file

Once configured, any push to the main branch will trigger automatic deployment to Azure.

## Azure Configuration

- Runtime: Python 3.12
- Web App Name: Netrunsystems
- Custom Domain: www.netrunsystems.com

## Contact

For any questions or support, please contact:
- Email: daniel@netrunsystems.com
- Phone: (805) 707-4828
