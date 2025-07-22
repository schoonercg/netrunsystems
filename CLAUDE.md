# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based corporate website for Netrun Systems, showcasing Azure governance solutions and various enterprise products. The application is designed for deployment on Azure App Service with automatic GitHub Actions deployment.

## Common Development Commands

### Python/Flask Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask application locally
python app.py

# Run tests
pytest tests/

# Run tests with coverage
pytest --cov=app tests/

# Format code with black
black app.py

# Lint code with flake8
flake8 app.py
```

### Node.js Server (Alternative)
```bash
# Install dependencies
npm install

# Run the Express server
npm start
```

## Architecture Overview

### Core Application Structure
- **app.py**: Main Flask application with all routes and business logic
  - Session-based authentication using Flask-Session
  - CSRF protection with Flask-WTF
  - Blog system with markdown support
  - Customer portal with authentication requirements
  - Multiple product pages and research project showcases

### Key Routes and Features
- **Public Pages**: Home, products, blog, contact, early access
- **Protected Portal**: `/portal/*` routes require authentication via `@requires_auth` decorator
- **Admin**: `/admin/blog` for blog management
- **Blog System**: Dynamic markdown-based blog posts stored in `/blog_posts/`

### Frontend Architecture
- **Templates**: Jinja2 templates in `/templates/` with base layout inheritance
- **Static Assets**: 
  - CSS: Custom styles in `/static/css/styles.css`
  - JavaScript: Main functionality in `/static/js/main.js` including dark mode toggle
  - Images: Product images and icons in `/static/images/`

### Configuration and Environment
- Secret key and configuration read from environment variables
- No separate config.py file - configuration is inline in app.py
- Session storage uses filesystem (Flask-Session)

### Testing Strategy
- Unit tests in `/tests/test_app.py`
- Tests cover public routes and authentication flows
- Use Flask test client for route testing
- Run individual tests with: `pytest tests/test_app.py::test_function_name`

### Deployment
- Configured for Azure App Service deployment
- GitHub Actions workflow for automatic deployment on push to main
- Runtime: Python 3.12
- Production domain: www.netrunsystems.com