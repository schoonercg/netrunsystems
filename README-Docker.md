# Docker Development Environment

This document provides instructions for running the Netrun Systems Flask application in a Docker environment for local development and testing.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

The application will be available at:
- http://localhost:8000 - Main application
- http://localhost:8000/health - Health check endpoint

### Option 2: Direct Docker

```bash
# Build the image
docker build -t netrun-app .

# Run the container
docker run -d --name netrun-app -p 8000:8000 netrun-app

# View logs
docker logs -f netrun-app

# Stop and remove container
docker stop netrun-app && docker rm netrun-app
```

## Configuration

### Environment Variables

The application supports the following environment variables:

- `FLASK_ENV`: Set to `development` for development mode (default in Docker)
- `SECRET_KEY`: Flask secret key (has default for development)
- `PORT`: Port to run the application on (default: 8000)
- `DEV_MODE`: Set to `true` to enable development features

### Azure Services (Optional)

For full functionality, you can configure Azure services:

- `AZURE_CLIENT_ID`: Azure AD application client ID
- `AZURE_CLIENT_SECRET`: Azure AD application client secret
- `AZURE_TENANT_ID`: Azure AD tenant ID
- `AZURE_EMAIL_CONNECTION_STRING`: Azure Communication Services connection string

## Development Features

### Hot Reload (Volume Mounting)

To enable hot reload during development, modify the docker-compose.yml to mount your source code:

```yaml
volumes:
  - .:/app
  - /app/flask_session  # Exclude session files
```

### Database and Sessions

- Sessions are stored in the filesystem (`flask_session/` directory)
- No external database required for basic functionality
- Blog posts are stored as Markdown files in `blog_posts/`

### Debugging

Access debug information at:
- http://localhost:8000/debug - Application debug info
- http://localhost:8000/health - Health check with timestamp

## Production Considerations

### Security

- Change the default `SECRET_KEY` in production
- Enable HTTPS termination at load balancer/reverse proxy
- Configure proper environment variables for Azure services
- Review security headers in `security.py`

### Performance

- The Docker configuration uses Gunicorn with 1 worker (suitable for development)
- For production, increase worker count based on CPU cores
- Consider using a reverse proxy (nginx configuration included)

### Monitoring

- Health check endpoint available for load balancer checks
- Logs are output to stdout/stderr for container log collection
- Application Insights integration available with Azure configuration

## Troubleshooting

### Common Issues

1. **Port 8000 already in use**
   ```bash
   # Find and stop process using port 8000
   lsof -ti:8000 | xargs kill -9
   # Or change port in docker-compose.yml
   ```

2. **Permission issues with flask_session**
   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER flask_session/
   ```

3. **Template errors about missing routes**
   - Ensure all routes referenced in templates are defined in app.py
   - Check that url_for() calls match actual route function names

### Logs and Debugging

```bash
# View application logs
docker-compose logs netrun-app

# Execute commands inside container
docker-compose exec netrun-app bash

# Check route registration
docker-compose exec netrun-app python -c "from app import app; print([str(rule) for rule in app.url_map.iter_rules()])"
```

## File Structure

```
/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore           # Files to exclude from Docker build
├── nginx.conf              # Optional nginx reverse proxy config
├── requirements_full.txt   # Python dependencies
└── app.py                  # Main Flask application
```

## Next Steps

1. **Azure Deployment**: Use the same Docker image for Azure Container Instances or Azure App Service containers
2. **CI/CD Integration**: Integrate with GitHub Actions for automated builds
3. **Monitoring**: Set up Application Insights and logging
4. **Scaling**: Configure horizontal scaling with multiple containers