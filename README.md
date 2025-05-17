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
- The application reads configuration from environment variables directly in
  `app.py`, so a separate `config.py` file is not required.

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

1. Fork or clone this repository to your GitHub account.
2. In the Azure Portal, navigate to your App Service and connect the repository via **Deployment Center > GitHub Actions**.
3. Create a service principal with access to the App Service.
4. Add secrets for the service principal credentials in your GitHub repository. The secret names must match those used in the workflow files:
   - `AZUREAPPSERVICE_CLIENTID_*`
   - `AZUREAPPSERVICE_TENANTID_*`
   - `AZUREAPPSERVICE_SUBSCRIPTIONID_*`
   These credentials are required for the provided workflows, which authenticate to Azure using OIDC.

Once configured, any push to the main branch will trigger automatic deployment to Azure.

## Azure Configuration

- Runtime: Python 3.12
- Web App Name: Netrunsystems
- Custom Domain: www.netrunsystems.com

## Contact

For any questions or support, please contact:
- Email: daniel@netrunsystems.com
- Phone: (805) 707-4828
