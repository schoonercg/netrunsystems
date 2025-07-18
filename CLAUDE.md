# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Local development
python app.py

# Production with Gunicorn
gunicorn --bind=0.0.0.0 --timeout 600 app:app
```

### Testing and Validation
```bash
# Install dependencies
pip install -r requirements.txt

# Run static type checking (if available)
python -m mypy app.py

# Run basic syntax check
python -m py_compile app.py
```

### Common Development Tasks
```bash
# Check for security issues
python -m bandit app.py

# Format code (if using black)
black app.py

# Run Flask development server
FLASK_ENV=development python app.py
```

## Architecture Overview

This is a Flask-based web application for Netrun Systems, a company providing Azure cloud management solutions. The application serves as the main corporate website with product pages, blog functionality, and customer portal features.

### Core Components

**Main Application (app.py)**
- Flask web application with 600+ lines of route handlers
- Implements Azure AD authentication using MSAL
- Email functionality through Azure Communication Services
- Blog system with Markdown support
- Customer portal with authentication
- Admin interface for blog management

**Configuration System (config.py)**
- Environment-based configuration classes
- Security headers configuration
- Azure service settings
- Development/staging/production configs

**Azure Integration (azure_utils.py)**
- Azure service manager for Key Vault, Blob Storage
- Azure Monitor/Application Insights integration
- Managed identity authentication
- Centralized Azure service operations

**Security (security.py)**
- Rate limiting with Flask-Limiter
- Security headers with Talisman
- Input validation and sanitization
- Azure AD authentication decorators

### Key Features

1. **Multi-Product Website**: Serves multiple product pages (Intirkon, Intirfix, Intirkast, etc.)
2. **Blog System**: Markdown-based blog with front matter parsing
3. **Customer Portal**: Authentication-protected customer resources
4. **Admin Panel**: Blog post creation and management
5. **Form Handling**: Contact forms, early access requests, RSVP system
6. **Azure Integration**: Email services, authentication, monitoring

### Template Structure

The application uses Jinja2 templates with a base template system:
- `base.html`: Common layout with navigation and footer
- Product pages: Individual templates for each product
- Blog templates: `blog.html` and `blog_post.html`
- Customer portal: Protected section with multiple pages
- Error pages: Custom 404 and 500 error handling

### Authentication Flow

1. **Customer Authentication**: Development mode auto-login or Azure AD
2. **Admin Authentication**: Azure AD OAuth flow with MSAL
3. **Session Management**: Filesystem-based sessions
4. **Security**: CSRF protection on all forms

### Environment Configuration

**Required Environment Variables:**
- `SECRET_KEY`: Flask secret key
- `FLASK_ENV`: Environment (development/staging/production)

**Optional Azure Services:**
- `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`: Azure AD authentication
- `AZURE_EMAIL_CONNECTION_STRING`: Azure Communication Services
- `AZURE_KEYVAULT_NAME`: Key Vault for secret management

## Development Patterns

### Adding New Routes
```python
@app.route('/new-page')
def new_page():
    now = datetime.datetime.now()
    return render_template('new_page.html', now=now)
```

### Form Handling Pattern
```python
@app.route('/form-page', methods=['GET', 'POST'])
def form_page():
    if request.method == 'POST':
        # Process form data
        # Send email notification
        # Flash success message
        return redirect(url_for('form_page'))
    return render_template('form_page.html')
```

### Email Service Usage
```python
# Send email through Azure Communication Services
send_email(
    to_address='recipient@example.com',
    subject='Subject',
    html_content='<p>HTML content</p>'
)
```

### Blog Post Management
- Blog posts are stored as Markdown files in `blog_posts/`
- Front matter format: title, author, date, slug, excerpt
- Admin interface at `/admin/blog` for creating posts
- Automatic slug generation from titles

## Security Considerations

- All forms require CSRF tokens
- Rate limiting on all endpoints
- Security headers configured
- Azure AD authentication for admin functions
- Input validation and sanitization
- Session security with filesystem storage

## Deployment

### Replit Deployment
- Primary hosting platform
- Configuration in `.replit` file
- Environment variables set through Replit interface

### Azure Web App Deployment
- GitHub Actions workflow configured
- Azure App Service deployment
- Environment variables configured in Azure portal

## File Structure

```
/
├── app.py                    # Main Flask application
├── config.py                 # Configuration classes
├── azure_utils.py            # Azure service integrations
├── security.py               # Security utilities
├── requirements.txt          # Python dependencies
├── templates/                # Jinja2 templates
├── static/                   # Static assets (CSS, JS, images)
├── blog_posts/               # Markdown blog posts
├── flask_session/            # Session storage
├── .replit                   # Replit configuration
├── .azure/                   # Azure deployment config
└── .github/workflows/        # GitHub Actions
```

## Common Issues and Solutions

### Template Errors
- Ensure all templates receive the `now` variable
- Check template inheritance and block structure
- Verify static file paths are correct

### Authentication Issues
- Check Azure AD configuration environment variables
- Verify redirect URIs match Azure app registration
- Check session configuration for authentication persistence

### Email Issues
- Verify Azure Communication Services connection string
- Check sender email is verified in Azure
- Log email failures for debugging

### Development vs Production
- Use `DEV_MODE` flag for development features
- Configure different settings for each environment
- Test with appropriate Azure service configurations

## Code Style and Conventions

- Follow Flask best practices
- Use consistent error handling with flash messages
- Include proper logging for debugging
- Maintain security-first approach
- Document complex business logic
- Use type hints where beneficial