
# Netrun Systems Technical Architecture & Standards Guide

## Table of Contents
1. [Overview](#overview)
2. [Technical Stack](#technical-stack)
3. [Architecture Patterns](#architecture-patterns)
4. [Style Guide](#style-guide)
5. [File Structure Standards](#file-structure-standards)
6. [Configuration Standards](#configuration-standards)
7. [Deployment Standards](#deployment-standards)
8. [Creating New Company Sites](#creating-new-company-sites)
9. [Security Standards](#security-standards)
10. [Best Practices](#best-practices)

## Overview

This document defines the technical architecture, design standards, and implementation patterns used across all Netrun Systems web properties. Follow these guidelines to ensure consistency, maintainability, and brand coherence across all company websites.

### Core Principles
- **Human-Centered Design**: Technology that empowers people
- **Community-Driven**: Built for real businesses and communities
- **Consistent Brand Experience**: Unified look and feel across all properties
- **Scalable Architecture**: Easy to extend and maintain
- **Security First**: Built-in security best practices

## Technical Stack

### Backend Framework
- **Flask 3.x** - Python web framework
- **Python 3.12+** - Runtime environment
- **Werkzeug** - WSGI utilities
- **Jinja2** - Template engine

### Frontend Technologies
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with CSS Grid and Flexbox
- **Vanilla JavaScript** - No frameworks for better performance
- **Progressive Enhancement** - Works without JavaScript

### Dependencies
```
Flask==3.0.0
Werkzeug==3.0.0
python-dotenv==1.0.0
azure-communication-email==1.0.0
msal==1.24.1
requests==2.31.0
markdown==3.5.1
flask-wtf==1.2.1
```

### Development Environment
- **Replit** - Primary development and hosting platform
- **Git** - Version control
- **GitHub Actions** - CI/CD (when needed)

## Architecture Patterns

### MVC Pattern
```
app.py (Controller)
├── Route handlers
├── Business logic
├── Authentication
└── Error handling

templates/ (View)
├── base.html (Base template)
├── Page templates
└── Component partials

static/ (Static Assets)
├── css/styles.css
├── js/main.js
└── images/
```

### Template Hierarchy
```
base.html
├── All page templates extend base.html
├── Consistent header/footer
├── Common meta tags and assets
└── Flash messaging system
```

### Configuration Management
```python
# config.py pattern
class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    # Common settings

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
```

## Style Guide

### Color Palette
```css
:root {
  --primary-color: #90b9ab;      /* Netrun Green */
  --secondary-color: #000000;     /* Black */
  --accent-color: #00AEEF;        /* Blue accent */
  --text-color: #fff;             /* White text */
  --light-gray: #f4f4f4;          /* Light background */
  --medium-gray: #ddd;            /* Medium gray */
  --dark-gray: #555;              /* Dark gray */
  --white: #f4f4f4;               /* Off-white */
  --success: #4caf50;             /* Success green */
  --error: #f44336;               /* Error red */
  --warning: #ff9800;             /* Warning orange */
  --info: #2196f3;                /* Info blue */
}
```

### Typography
```css
/* Primary font stack */
font-family: 'Futura', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;

/* Font weights */
--font-normal: 400;
--font-medium: 500;
--font-bold: 700;

/* Font sizes */
--font-small: 0.875rem;
--font-base: 1rem;
--font-large: 1.125rem;
--font-xl: 1.25rem;
--font-2xl: 1.5rem;
--font-3xl: 2rem;
```

### Component Standards

#### Buttons
```css
.btn {
  display: inline-block;
  padding: 12px 24px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.btn.primary {
  background-color: var(--primary-color);
  color: var(--white);
  border: none;
}

.btn.secondary {
  background-color: transparent;
  color: var(--primary-color);
  border: 2px solid var(--primary-color);
}
```

#### Cards
```css
.feature-card, .product-card {
  background-color: #000000;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
  border: 1px solid rgba(144, 185, 171, 0.2);
  color: #ffffff;
  text-align: left;
  padding: 1.5rem;
  position: relative;
}
```

### Layout Standards
- **Container max-width**: 1200px
- **Grid gaps**: 2rem standard, 1.5rem mobile
- **Section padding**: 4rem desktop, 2rem mobile
- **Border radius**: 8px for cards, 4px for buttons

## File Structure Standards

### Required Directory Structure
```
project-root/
├── app.py                    # Main application file
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── .replit                   # Replit configuration
├── static/
│   ├── css/
│   │   └── styles.css        # Main stylesheet
│   ├── js/
│   │   └── main.js          # Main JavaScript
│   ├── images/              # Image assets
│   └── favicon.ico          # Site favicon
├── templates/
│   ├── base.html            # Base template
│   ├── index.html           # Homepage
│   ├── about.html           # About page
│   ├── contact.html         # Contact page
│   ├── 404.html             # Error pages
│   └── 500.html
├── blog_posts/              # Markdown blog posts
├── docs/                    # Documentation
└── flask_session/           # Session storage
```

### File Naming Conventions
- **Templates**: lowercase with underscores (`about_us.html`)
- **Routes**: lowercase with hyphens (`/about-us`)
- **CSS classes**: lowercase with hyphens (`.hero-section`)
- **Images**: descriptive names (`company-logo.png`)

## Configuration Standards

### Environment Variables
```python
# Required environment variables
SECRET_KEY=your-secret-key-here
FLASK_ENV=development|production

# Azure Communication Services (optional)
AZURE_COMMUNICATION_SERVICES_CONNECTION_STRING=your-connection-string
AZURE_COMMUNICATION_SERVICES_SENDER_EMAIL=noreply@yourdomain.com

# Azure Entra ID (optional)
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
AZURE_REDIRECT_URI=/auth/callback
```

### Flask Configuration
```python
# Standard Flask app initialization
app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

# Required extensions
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

## Deployment Standards

### Replit Deployment
1. **Workflow Configuration**:
```yaml
# .replit file should contain:
run = "python app.py"
entrypoint = "app.py"

[deployment]
run = ["python", "app.py"]
build = []
```

2. **Production Settings**:
```python
# For production deployment
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
```

## Creating New Company Sites

### 1. Repository Setup
```bash
# Clone the base template
git clone [base-template-repo] new-site-name
cd new-site-name

# Update configuration
# Edit config.py with new site details
# Update environment variables
```

### 2. Customization Checklist
- [ ] Update `app.py` with new site name and routes
- [ ] Modify `config.py` with site-specific settings
- [ ] Replace logo and images in `static/images/`
- [ ] Update `base.html` with new site title and navigation
- [ ] Customize homepage content in `index.html`
- [ ] Update footer links and contact information
- [ ] Configure environment variables

### 3. Brand Customization
```css
/* Site-specific color overrides in styles.css */
:root {
  --primary-color: #your-brand-color;
  --accent-color: #your-accent-color;
}

/* Site-specific fonts if needed */
@import url('https://fonts.googleapis.com/css2?family=Your-Font');

body {
  font-family: 'Your-Font', 'Futura', sans-serif;
}
```

### 4. Content Management
- Use the same blog post structure in `blog_posts/`
- Follow the same template patterns for new pages
- Maintain consistent navigation structure
- Use the same form handling patterns

## Security Standards

### CSRF Protection
```python
# Always include CSRF protection
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# In templates
<form method="POST">
    {{ csrf_token() }}
    <!-- form content -->
</form>
```

### Headers Security
```python
# Security headers configuration
SECURITY_HEADERS = {
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'SAMEORIGIN',
    'X-XSS-Protection': '1; mode=block',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
}
```

### Session Security
```python
# Session configuration
SESSION_TYPE = 'filesystem'
SESSION_COOKIE_SECURE = True  # Production only
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

## Best Practices

### Code Organization
1. **Single Responsibility**: Each function/route has one purpose
2. **DRY Principle**: Reuse common functionality
3. **Clear Naming**: Self-documenting code
4. **Error Handling**: Graceful error handling throughout

### Performance
1. **Image Optimization**: Compress images, use appropriate formats
2. **CSS/JS Minification**: Minify assets for production
3. **Caching**: Implement appropriate caching strategies
4. **Database Queries**: Optimize when using databases

### Accessibility
1. **Semantic HTML**: Use proper HTML5 elements
2. **Alt Text**: All images have descriptive alt text
3. **Color Contrast**: Meet WCAG 2.1 AA standards
4. **Keyboard Navigation**: All interactive elements accessible via keyboard

### Mobile Responsiveness
```css
/* Mobile-first responsive design */
@media (max-width: 768px) {
  .nav-links {
    flex-direction: column;
  }
  
  .hero h1 {
    font-size: 1.8rem;
  }
}
```

### Testing Checklist
- [ ] All pages load without errors
- [ ] Forms submit correctly
- [ ] Navigation works on all devices
- [ ] Images load and display properly
- [ ] Contact forms send emails
- [ ] Error pages display correctly
- [ ] Mobile responsiveness
- [ ] Cross-browser compatibility

### Maintenance
1. **Regular Updates**: Keep dependencies updated
2. **Security Monitoring**: Monitor for security issues
3. **Performance Monitoring**: Track site performance
4. **Backup Strategy**: Regular backups of content and configuration

## Troubleshooting Common Issues

### Template Errors
```python
# Missing 'now' variable in templates
def route_handler():
    now = datetime.datetime.now()
    return render_template('template.html', now=now)
```

### Static Files Not Loading
```python
# Ensure proper static file configuration
app = Flask(__name__, static_folder='static', static_url_path='/static')
```

### Email Issues
```python
# Check Azure Communication Services configuration
if not connection_string:
    app.logger.info("Email service not configured, logging instead")
    return
```

## Version History
- **v1.0** - Initial architecture document
- **Date**: Created based on Netrun Systems website architecture

---

*This document should be updated whenever architectural changes are made to maintain consistency across all company web properties.*
