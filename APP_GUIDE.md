# Home Secrets Add-on: Application Developer Guide

This guide explains how to integrate your application with the Home Secrets Add-on to securely manage secrets and Google OAuth tokens.

## Prerequisites

1. **Home Assistant running** with the Home Secrets Add-on installed and started
2. **Add-on configured** with your API key and secrets (see Configuration section)
3. **Network access** to your Home Assistant instance from your application

## Configuration Setup

### 1. Configure the Add-on

In Home Assistant → Settings → Add-ons → Home Secrets Server → Configuration:

```yaml
api_key: "your-secure-api-key-here"        # Required for all API calls
cors_allowed_origins:
  - "http://localhost:3000"                # Add your app's origin
  - "http://your-app-domain.com"
secret_prefix: "HS_"                       # Only HS_* env vars are accessible
extra_env:
  HS_OPENAI_API_KEY: "sk-your-openai-key"  # Add your secrets here
  HS_GOOGLE_SHEETS_KEY: "your-sheets-key"
  HS_DATABASE_URL: "your-db-connection"
google:
  enabled: true                            # Enable if using OAuth
  client_id: "your-oauth-client-id"
  client_secret: "your-oauth-client-secret"
  scopes:
    - "https://www.googleapis.com/auth/drive.readonly"
    - "https://www.googleapis.com/auth/spreadsheets"
  redirect_bases:                          # Multiple redirect URLs (register ALL in Google Console)
    - "http://your-ha-ip:8126"             # Home Assistant local network
    - "https://rossgrambo.github.io/toddler-lunch"  # Production domain
    - "http://localhost:8000"              # Local development
```

### 2. Find Your Home Assistant IP

- Check your Home Assistant URL (e.g., `http://192.168.1.100:8123`)
- The secrets server runs on the same IP, port 8126
- Example: `http://192.168.1.100:8126`

## Secret Management

### Retrieving Secrets

**Endpoint**: `GET /secret/{key}`

**Headers Required**:
```
X-API-Key: your-secure-api-key-here
```

**Examples**:

```javascript
// JavaScript/Node.js
async function getSecret(secretName) {
  const response = await fetch(`http://homeassistant.local:8126/secret/${secretName}`, {
    headers: {
      'X-API-Key': 'your-secure-api-key-here'
    }
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get secret: ${response.status}`);
  }
  
  const data = await response.json();
  return data.value;
}

// Usage
const openaiKey = await getSecret('OPENAI_API_KEY');  // Gets HS_OPENAI_API_KEY
const dbUrl = await getSecret('DATABASE_URL');        // Gets HS_DATABASE_URL
```

```python
# Python
import requests

def get_secret(secret_name, api_key, ha_ip="homeassistant.local"):
    url = f"http://{ha_ip}:8126/secret/{secret_name}"
    headers = {"X-API-Key": api_key}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()["value"]

# Usage
openai_key = get_secret("OPENAI_API_KEY", "your-api-key")
db_url = get_secret("DATABASE_URL", "your-api-key")
```

```bash
# cURL
curl -H "X-API-Key: your-secure-api-key-here" \
     http://homeassistant.local:8126/secret/OPENAI_API_KEY
```

**Response Format**:
```json
{
  "key": "OPENAI_API_KEY",
  "env": "HS_OPENAI_API_KEY", 
  "value": "sk-your-actual-secret-value"
}
```

**Important Notes**:
- Secret names are automatically prefixed (e.g., `OPENAI_API_KEY` → `HS_OPENAI_API_KEY`)
- Only secrets with the configured prefix are accessible
- Returns 404 if secret doesn't exist
- Returns 403 if API key is invalid

## Google OAuth Integration

### 1. Initial Setup (One-time)

First, a user must authorize your application through the browser:

```javascript
// Step 1: Get authorization URL
async function startGoogleAuth() {
  const response = await fetch('http://homeassistant.local:8126/oauth/google/start', {
    headers: {
      'X-API-Key': 'your-secure-api-key-here'
    }
  });
  
  const data = await response.json();
  console.log('Visit this URL to authorize:', data.authorize_url);
  
  // User visits the URL, completes OAuth, gets redirected back
  // The system automatically stores the refresh token
}
```

### 2. Getting Access Tokens

Once authorized, your application can get fresh access tokens:

**Endpoint**: `GET /oauth/google/token`

**Headers Required**:
```
X-API-Key: your-secure-api-key-here
```

```javascript
// JavaScript/Node.js
async function getGoogleToken() {
  const response = await fetch('http://homeassistant.local:8126/oauth/google/token', {
    headers: {
      'X-API-Key': 'your-secure-api-key-here'  // REQUIRED!
    }
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get token: ${response.status}`);
  }
  
  const data = await response.json();
  return data.access_token;
}

// Usage
const accessToken = await getGoogleToken();

// Use with Google APIs
const sheetsResponse = await fetch('https://sheets.googleapis.com/v4/spreadsheets/your-sheet-id', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
```

```python
# Python
def get_google_token(api_key, ha_ip="homeassistant.local"):
    url = f"http://{ha_ip}:8126/oauth/google/token"
    headers = {"X-API-Key": api_key}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()["access_token"]

# Usage
access_token = get_google_token("your-api-key")

# Use with Google APIs
headers = {"Authorization": f"Bearer {access_token}"}
sheets_response = requests.get(
    "https://sheets.googleapis.com/v4/spreadsheets/your-sheet-id",
    headers=headers
)
```

**Response Format**:
```json
{
  "access_token": "ya29.a0ARrdaM...",
  "expiry": 1694728800,
  "token_type": "Bearer",
  "scope": "https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/spreadsheets"
}
```

### 3. Token Management

- **Automatic Refresh**: The system automatically refreshes expired tokens
- **Expiry Handling**: Check the `expiry` timestamp (Unix time) to avoid unnecessary calls
- **Error Handling**: If you get a 409 error, the refresh token is missing and re-authorization is needed

## Complete Application Examples

### Node.js Application

```javascript
class HomeSecretsClient {
  constructor(haHost = 'homeassistant.local', apiKey) {
    this.baseUrl = `http://${haHost}:8126`;
    this.apiKey = apiKey;
  }
  
  async getSecret(secretName) {
    const response = await fetch(`${this.baseUrl}/secret/${secretName}`, {
      headers: { 'X-API-Key': this.apiKey }
    });
    
    if (!response.ok) {
      throw new Error(`Failed to get secret ${secretName}: ${response.status}`);
    }
    
    const data = await response.json();
    return data.value;
  }
  
  async getGoogleToken() {
    const response = await fetch(`${this.baseUrl}/oauth/google/token`, {
      headers: { 'X-API-Key': this.apiKey }
    });
    
    if (!response.ok) {
      throw new Error(`Failed to get Google token: ${response.status}`);
    }
    
    const data = await response.json();
    return data.access_token;
  }
}

// Usage
const secrets = new HomeSecretsClient('192.168.1.100', 'your-api-key');

async function main() {
  try {
    // Get secrets
    const openaiKey = await secrets.getSecret('OPENAI_API_KEY');
    const dbUrl = await secrets.getSecret('DATABASE_URL');
    
    // Get Google token for API calls
    const googleToken = await secrets.getGoogleToken();
    
    // Use in your application
    console.log('Secrets loaded successfully');
  } catch (error) {
    console.error('Failed to load secrets:', error);
    process.exit(1);
  }
}

main();
```

### Python Application

```python
import requests
from typing import Optional

class HomeSecretsClient:
    def __init__(self, ha_host: str = "homeassistant.local", api_key: str):
        self.base_url = f"http://{ha_host}:8126"
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key}
    
    def get_secret(self, secret_name: str) -> str:
        """Get a secret value by name."""
        url = f"{self.base_url}/secret/{secret_name}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()["value"]
    
    def get_google_token(self) -> str:
        """Get a fresh Google OAuth access token."""
        url = f"{self.base_url}/oauth/google/token"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()["access_token"]

# Usage
def main():
    secrets = HomeSecretsClient("192.168.1.100", "your-api-key")
    
    try:
        # Load secrets
        openai_key = secrets.get_secret("OPENAI_API_KEY")
        db_url = secrets.get_secret("DATABASE_URL")
        
        # Get Google token
        google_token = secrets.get_google_token()
        
        print("Secrets loaded successfully")
        
    except requests.RequestException as e:
        print(f"Failed to load secrets: {e}")
        exit(1)

if __name__ == "__main__":
    main()
```

## Health Check & Debugging

### Basic Service Test

Test if the service is running:

```bash
curl http://homeassistant.local:8126/healthz
```

Expected response: `{"status": "ok"}`

### Debug OAuth Endpoints

Test OAuth endpoints with proper headers:

```bash
# Test token endpoint (should return token or error, not 404)
curl -H "X-API-Key: your-api-key-here" \
     http://homeassistant.local:8126/oauth/google/token

# Test start endpoint  
curl -H "X-API-Key: your-api-key-here" \
     http://homeassistant.local:8126/oauth/google/start
```

**Common responses**:
- `404 Not Found`: Missing X-API-Key header or Google OAuth disabled
- `403 Forbidden`: Wrong API key
- `409 Conflict`: No refresh token stored (need to run /start first)
- `500 Internal Server Error`: Missing Google client credentials

## Troubleshooting

### Common Issues

1. **"This site can't be reached"**
   - Check Home Assistant IP address
   - Ensure add-on is started
   - Try `http://IP:8126/healthz`

2. **403 Forbidden**
   - Verify API key in both add-on config and your requests
   - Check X-API-Key header format

3. **404 Not Found (secrets)**
   - Verify secret exists in add-on configuration
   - Check secret name matches (without HS_ prefix)
   - Ensure secret has a non-empty value

4. **404 Not Found (OAuth endpoints)**
   - Missing `X-API-Key` header in request
   - Google OAuth not enabled in add-on config (`google.enabled: false`)
   - Check that the endpoint URL is correct

5. **409 Conflict (Google OAuth)**
   - Refresh token expired or missing
   - Re-run the initial authorization flow

6. **CORS errors (web apps)**
   - Add your domain to `cors_allowed_origins` in add-on config
   - Use full URL with protocol (e.g., `http://localhost:3000`)

### Google Cloud Console Setup (OAuth)

When using Google OAuth with multiple redirect URLs, you must register ALL redirect URIs in Google Cloud Console:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project → APIs & Services → Credentials
3. Edit your OAuth 2.0 Client ID
4. Add all redirect URIs from your config:
   ```
   http://your-ha-ip:8126/oauth/google/callback
   https://rossgrambo.github.io/toddler-lunch/oauth/google/callback
   http://localhost:8000/oauth/google/callback
   ```
5. Save the configuration

**Note**: The system will use the first URL in `redirect_bases` as the primary redirect URI for OAuth flow.

### Network Configuration

- **Local Network**: Use Home Assistant's local IP address
- **Docker/Container**: May need to use host networking or bridge configuration
- **Reverse Proxy**: Configure proxy to forward requests to port 8126
- **Firewall**: Ensure port 8126 is accessible from your application's network

This system provides secure, centralized secret management for your Home Assistant environment without exposing sensitive data in your application code.