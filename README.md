# Home Secrets Add-on Repository

This repository provides a Home Assistant add-on for secure secret management and Google OAuth integration for LAN applications.

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Frossgrambo%2Fhome-secrets-addon)

## Add-ons

This repository contains the following add-ons:

### [Home Secrets Server](./addons/home-secrets)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield] 
![Supports armv7 Architecture][armv7-shield]

_Local secret/key server + Google OAuth/refresh for LAN apps._

## Installation

1. Add this repository to your Home Assistant instance:
   - Go to Settings → Add-ons → Add-on store → ⋮ → Repositories  
   - Add: `https://github.com/rossgrambo/home-secrets-addon`

2. Install the "Home Secrets Server" add-on

3. Configure and start the add-on

> **Note**: During initial setup, the add-on builds locally. See [GHCR_SETUP.md](./GHCR_SETUP.md) for automated build configuration.

## Features

- **Secure Secret Management**: API-key protected secret retrieval for your applications
- **Google OAuth Integration**: Complete OAuth flow with automatic token refresh
- **Git Sync**: Optional repository synchronization for dynamic code updates
- **CORS Support**: Configurable cross-origin access for web apps
- **Persistent Storage**: Tokens and data survive restarts

## Usage Example

```javascript
// Retrieve a secret
const response = await fetch("http://your-ha-ip:8126/secret/GOOGLE_API_KEY", {
  headers: { "X-API-Key": "your-api-key" }
});
const { value } = await response.json();

// Get Google OAuth token
const tokenResponse = await fetch("http://your-ha-ip:8126/oauth/google/token", {
  headers: { "X-API-Key": "your-api-key" }
});
const { access_token } = await tokenResponse.json();
```

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg