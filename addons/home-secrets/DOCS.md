# Home Assistant Add-on: Home Secrets Server

## Overview

The Home Secrets Server add-on provides a secure, local API for managing secrets and handling Google OAuth flows for your Home Assistant environment and LAN applications.

## Features

### Secret Management
- Store secrets as environment variables with a configurable prefix
- Secure API key-based authentication for all requests
- Support for dynamic secret injection via add-on configuration

### Google OAuth Integration
- Complete OAuth 2.0 authorization code flow
- Automatic token refresh functionality
- Secure token storage that persists across restarts
- Support for multiple OAuth scopes

### Developer Features
- Optional Git repository synchronization for dynamic code updates
- CORS configuration for web application integration
- FastAPI-based REST API with automatic documentation
- Health check endpoint for monitoring

## API Endpoints

### Secret Retrieval
- **GET** `/secret/{key}` - Retrieve a secret value
  - Headers: `X-API-Key: your-api-key`
  - Returns: `{"key": "KEY_NAME", "env": "HS_KEY_NAME", "value": "secret-value"}`

### Google OAuth
- **GET** `/oauth/google/start` - Initialize OAuth flow
  - Headers: `X-API-Key: your-api-key`
  - Returns: Authorization URL for user to visit

- **GET** `/oauth/google/callback` - OAuth callback (called by Google)
  - Query params: `code`, `state`
  - Returns: Success confirmation

- **GET** `/oauth/google/token` - Get current access token
  - Headers: `X-API-Key: your-api-key`
  - Query params: `label` (optional)
  - Returns: Current access token with expiry information

### System
- **GET** `/healthz` - Health check endpoint

## Configuration

### Required Settings

- **api_key**: Secret key required in `X-API-Key` header for all requests
- **secret_prefix**: Prefix for environment variables (e.g., "HS_" means only HS_* vars are accessible)

### CORS Configuration

- **cors_allowed_origins**: List of allowed origins for CORS
  - Use full URLs with scheme (e.g., `http://localhost:3000`)
  - CIDR notation in config is ignored; list concrete origins

### Secret Storage

- **extra_env**: Key-value pairs of secrets to make available
  - Keys should include your prefix (e.g., `HS_GOOGLE_API_KEY`)
  - Values are the actual secret values

### Google OAuth Setup

1. Create OAuth credentials in Google Cloud Console
2. Add your redirect URI: `http://your-ha-ip:8126/oauth/google/callback`
3. Configure the add-on with your client ID and secret
4. Set desired scopes for your application needs

### Git Sync (Optional)

- **enabled**: Enable/disable Git synchronization
- **repo**: Git repository URL to clone
- **branch**: Branch to checkout
- **subdir**: Subdirectory within repo (if app code is in a subfolder)

When enabled, the add-on will clone/update the repository at startup and run code from there instead of the built-in application.

## Security Considerations

- All API endpoints require authentication via `X-API-Key` header
- OAuth tokens are stored encrypted in the add-on's persistent storage
- Secrets are only accessible via the configured prefix system
- CORS is configurable to limit web application access
- Git sync supports private repositories (configure Git credentials as needed)

## Troubleshooting

### Common Issues

1. **OAuth callback fails**: Ensure redirect URI in Google Console exactly matches your configuration
2. **CORS errors**: Add your web app's full URL to `cors_allowed_origins`
3. **Secret not found**: Verify the secret key includes your configured prefix
4. **Git sync fails**: Check repository URL and ensure any required authentication is configured

### Logs

Monitor add-on logs for detailed error messages and startup information. The service logs all major operations including OAuth flows and secret access attempts.