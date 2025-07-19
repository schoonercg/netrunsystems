# Subdomain Setup Guide

## Overview

The Flask application now supports subdomain routing for `rsvp.netrunsystems.com` and proper handling of `www.netrunsystems.com`.

## Implemented Features

### 1. RSVP Subdomain (`rsvp.netrunsystems.com`)
- **Root path (`/`)**: Redirects to `/rsvp` page
- **RSVP path (`/rsvp`)**: Serves the RSVP page normally
- **Any other path**: Redirects to `/rsvp` page
- **Purpose**: Dedicated subdomain for event RSVP functionality

### 2. WWW Subdomain (`www.netrunsystems.com`)
- **All paths**: 301 permanent redirect to `https://netrunsystems.com` 
- **Query strings preserved**: `www.netrunsystems.com/about?ref=test` → `https://netrunsystems.com/about?ref=test`
- **Purpose**: SEO-friendly canonical URL structure

### 3. Other Subdomains
- **Any other subdomain**: 301 redirect to main domain
- **Examples**: `api.netrunsystems.com`, `blog.netrunsystems.com` → `https://netrunsystems.com`

## Implementation Details

### Flask Middleware
```python
@app.before_request
def handle_subdomain():
    """Handle subdomain routing for rsvp.netrunsystems.com and www redirects"""
    host = request.headers.get('Host', '').lower()
    
    # RSVP subdomain logic
    # WWW redirect logic  
    # Other subdomain handling
```

### Logging
- All subdomain routing decisions are logged to Application Insights
- Log messages include host, path, and action taken
- Helpful for debugging and monitoring traffic patterns

## DNS Configuration Required

To fully enable this functionality, configure DNS records:

### 1. RSVP Subdomain
```
Type: CNAME
Name: rsvp
Value: netrun.azurewebsites.net
```

### 2. WWW Subdomain  
```
Type: CNAME
Name: www
Value: netrun.azurewebsites.net
```

### 3. Azure App Service Custom Domains
In Azure Portal → App Service → Custom domains:
1. Add `rsvp.netrunsystems.com`
2. Add `www.netrunsystems.com`
3. Configure SSL certificates for both domains

## Testing

### Manual Testing URLs
1. `https://rsvp.netrunsystems.com/` → Should redirect to RSVP page
2. `https://rsvp.netrunsystems.com/about` → Should redirect to RSVP page  
3. `https://www.netrunsystems.com/` → Should redirect to `https://netrunsystems.com/`
4. `https://www.netrunsystems.com/about` → Should redirect to `https://netrunsystems.com/about`

### Automated Testing
Run the test script to validate routing logic:
```bash
python3 test_domain_routing.py
```

### Azure Logs
Monitor Application Insights or Azure App Service logs for routing messages:
- `RSVP subdomain accessed: /`
- `WWW subdomain accessed: /, redirecting to main domain`
- `Unknown subdomain ... accessed, redirecting to main domain`

## Benefits

### 1. SEO Optimization
- Single canonical domain (`netrunsystems.com`) prevents duplicate content issues
- 301 redirects preserve link equity and search rankings
- Clean URL structure for better user experience

### 2. Event Marketing
- Memorable RSVP URL: `rsvp.netrunsystems.com`
- Simplified marketing materials and email campaigns
- Direct routing to event registration

### 3. Scalability
- Framework for future subdomains (blog, api, etc.)
- Centralized routing logic for easy maintenance
- Consistent redirect behavior across all subdomains

## CORS Configuration

The application already supports subdomain CORS in `.azure/config.yml`:
```yaml
security:
  cors:
    allowedOrigins:
      - https://*.netrunsystems.com
      - https://*.azurewebsites.net
```

## Troubleshooting

### Common Issues

1. **DNS Propagation**: DNS changes can take 24-48 hours to fully propagate
2. **SSL Certificates**: Ensure SSL certificates are configured for all custom domains
3. **Redirect Loops**: Check Azure App Service logs if experiencing redirect loops

### Debug Steps

1. Check DNS resolution: `nslookup rsvp.netrunsystems.com`
2. Test with curl: `curl -I https://rsvp.netrunsystems.com/`
3. Review Azure App Service logs for routing messages
4. Verify custom domain configuration in Azure Portal

## Security Considerations

- All redirects use HTTPS
- CORS properly configured for subdomain access
- Same security headers applied across all domains
- No sensitive information exposed in redirect URLs

---

**Last Updated**: July 19, 2025  
**Implementation Status**: ✅ Complete - Ready for DNS configuration