# Home Assistant Add-on: Home Secrets Server

_Local secret/key server + Google OAuth/refresh for LAN apps._

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armv7 Architecture][armv7-shield]

## About

This add-on provides a local secrets management server with Google OAuth integration for your Home Assistant environment. It allows your LAN applications to securely retrieve secrets and obtain Google OAuth tokens without exposing sensitive information in your code.

## Features

- **Secure Secret Storage**: Store and retrieve secrets with API key authentication
- **Google OAuth Integration**: Complete OAuth flow with automatic token refresh
- **Git Sync**: Optional synchronization with Git repositories for dynamic code updates
- **CORS Support**: Configurable CORS for web applications
- **Persistent Storage**: Tokens and data survive add-on restarts

## Installation

1. Add this repository URL to your Home Assistant instance:
   - Go to Settings → Add-ons → Add-on store → ⋮ → Repositories
   - Add: `https://github.com/rossgrambo/home-secrets-addon`

2. Install the "Home Secrets Server" add-on

3. Configure the add-on options (see Configuration section)

4. Start the add-on

## Configuration

Add-on configuration:

```yaml
api_key: "your-secure-api-key-here"
cors_allowed_origins:
  - "http://localhost:3000"
  - "http://192.168.1.100:8080"
secret_prefix: "HS_"
extra_env:
  HS_GOOGLE_SHEETS_KEY: "your-google-sheets-api-key"
  HS_OPENAI_API_KEY: "your-openai-api-key"
google:
  enabled: true
  client_id: "your-google-oauth-client-id"
  client_secret: "your-google-oauth-client-secret"
  scopes:
    - "https://www.googleapis.com/auth/drive.readonly"
    - "openid"
    - "email"
  redirect_base: "http://192.168.1.20:8126"
```

## Usage

### Retrieving Secrets

```javascript
const response = await fetch("http://192.168.1.20:8126/secret/GOOGLE_SHEETS_KEY", {
  headers: { "X-API-Key": "your-api-key" }
});
const { value } = await response.json();
```

### Google OAuth Flow

1. Start OAuth: `GET /oauth/google/start` (with X-API-Key header)
2. User completes authorization in browser
3. Get access token: `GET /oauth/google/token` (with X-API-Key header)

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg