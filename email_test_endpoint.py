# Add this endpoint to your app.py file to test email configuration

@app.route('/test-email-config')
def test_email_config():
    """Test endpoint to check email configuration and send a test email"""
    if not session.get('admin'):
        return {'error': 'Unauthorized'}, 401
    
    config_check = {
        'timestamp': datetime.datetime.now().isoformat(),
        'configuration': {
            'service_principal': {
                'client_id_set': bool(AZURE_CLIENT_ID),
                'client_secret_set': bool(AZURE_CLIENT_SECRET),
                'tenant_id_set': bool(AZURE_TENANT_ID),
                'all_set': all([AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID])
            },
            'communication_service': {
                'endpoint_set': bool(AZURE_COMMUNICATION_SERVICE_ENDPOINT),
                'endpoint_value': AZURE_COMMUNICATION_SERVICE_ENDPOINT[:50] + '...' if AZURE_COMMUNICATION_SERVICE_ENDPOINT else 'NOT SET',
                'sender_email': AZURE_EMAIL_SENDER,
                'company_email': COMPANY_EMAIL,
                'early_access_email': EARLY_ACCESS_EMAIL
            },
            'packages': {
                'email_client_available': EmailClient is not None,
                'azure_identity_available': AZURE_IDENTITY_AVAILABLE,
                'can_send_emails': EmailClient is not None and AZURE_IDENTITY_AVAILABLE
            },
            'legacy': {
                'connection_string_set': bool(os.environ.get('AZURE_EMAIL_CONNECTION_STRING', '')),
                'warning': 'Connection string detected - should be removed!' if os.environ.get('AZURE_EMAIL_CONNECTION_STRING') else None
            }
        },
        'diagnostics': []
    }
    
    # Run diagnostics
    if not all([AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID]):
        config_check['diagnostics'].append({
            'level': 'error',
            'message': 'Service principal credentials not fully configured',
            'fix': 'Set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID environment variables'
        })
    
    if not AZURE_COMMUNICATION_SERVICE_ENDPOINT:
        config_check['diagnostics'].append({
            'level': 'error',
            'message': 'Communication service endpoint not configured',
            'fix': 'Set AZURE_COMMUNICATION_SERVICE_ENDPOINT environment variable'
        })
    elif not AZURE_COMMUNICATION_SERVICE_ENDPOINT.startswith('https://'):
        config_check['diagnostics'].append({
            'level': 'warning',
            'message': 'Endpoint should start with https://',
            'current': AZURE_COMMUNICATION_SERVICE_ENDPOINT
        })
    
    if os.environ.get('AZURE_EMAIL_CONNECTION_STRING'):
        config_check['diagnostics'].append({
            'level': 'warning',
            'message': 'Old connection string still present',
            'fix': 'Remove AZURE_EMAIL_CONNECTION_STRING and use service principal authentication'
        })
    
    if not EmailClient or not AZURE_IDENTITY_AVAILABLE:
        config_check['diagnostics'].append({
            'level': 'error',
            'message': 'Required packages not available',
            'fix': 'Install azure-communication-email and azure-identity packages'
        })
    
    # Test email sending if requested
    if request.args.get('send_test') == 'true':
        test_email = request.args.get('email', COMPANY_EMAIL)
        config_check['email_test'] = {
            'recipient': test_email,
            'attempting': True
        }
        
        try:
            html_content = f"""
                <h2>🧪 Email Configuration Test</h2>
                <p>This is a test email from the Netrunmail service.</p>
                <div style="background: #f0f8ff; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <h3>Configuration Details:</h3>
                    <ul>
                        <li><strong>Sender:</strong> {AZURE_EMAIL_SENDER}</li>
                        <li><strong>Endpoint:</strong> {AZURE_COMMUNICATION_SERVICE_ENDPOINT[:50]}...</li>
                        <li><strong>Time:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                        <li><strong>Service Principal:</strong> {'✅ Configured' if all([AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID]) else '❌ Not configured'}</li>
                    </ul>
                </div>
                <p>If you received this email, the email service is working correctly!</p>
            """
            
            success = send_email(
                to_address=test_email,
                subject="Email Configuration Test",
                html_content=html_content,
                plain_text_content="This is a test email from Netrunmail. Configuration test successful!"
            )
            
            config_check['email_test']['success'] = success
            config_check['email_test']['message'] = 'Email sent successfully!' if success else 'Email send failed - check logs'
            
        except Exception as e:
            config_check['email_test']['success'] = False
            config_check['email_test']['error'] = str(e)
            logger.error(f"Test email failed: {e}")
    
    # Add recommendations
    config_check['recommendations'] = []
    
    if len(config_check['diagnostics']) == 0:
        config_check['status'] = 'ready'
        config_check['recommendations'].append('Configuration looks good! Try sending a test email with ?send_test=true&email=your@email.com')
    else:
        config_check['status'] = 'issues_found'
        config_check['recommendations'].append('Fix the issues listed in diagnostics before testing email sending')
    
    return config_check, 200