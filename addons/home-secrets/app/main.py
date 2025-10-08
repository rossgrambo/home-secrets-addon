import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .secrets_api import router as secrets_router
from .oauth_google import router as google_router

app = FastAPI(title="Home Secrets Server", version="0.1.0")

# CORS
allowed_origins = []
raw = os.getenv("HS_CORS_ALLOWED_ORIGINS", "")
if raw:
    # Only accept concrete origins with scheme://host[:port]
    # If you put a CIDR in config, ignore it here; list concrete web origins you use.
    allowed_origins = [o.strip() for o in raw.split(",") if "://" in o]

# Allow all origins for OAuth endpoints to prevent CORS issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for OAuth functionality
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(secrets_router, prefix="")
app.include_router(google_router, prefix="")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/oauth", response_class=HTMLResponse)
def oauth_ui(request: Request):
    """OAuth management UI for easy token refresh"""
    base_url = str(request.base_url).rstrip('/')
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Home Secrets - OAuth Management</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }}
            .status {{ padding: 15px; margin: 20px 0; border-radius: 5px; font-weight: bold; }}
            .status.ok {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
            .status.error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
            .status.warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }}
            button {{ background: #007acc; color: white; border: none; padding: 12px 24px; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 10px 5px; }}
            button:hover {{ background: #005999; }}
            button:disabled {{ background: #ccc; cursor: not-allowed; }}
            .form-group {{ margin: 20px 0; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }}
            .code {{ background: #f1f1f1; padding: 10px; border-radius: 4px; font-family: monospace; margin: 10px 0; }}
            .section {{ margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 Home Secrets - OAuth Management</h1>
            
            <div id="status-section" class="section">
                <h2>Token Status</h2>
                <div id="status-display">Loading...</div>
                <button onclick="checkStatus()">Refresh Status</button>
            </div>

            <div class="section">
                <h2>🔑 API Key Required</h2>
                <div class="form-group">
                    <label for="api-key">API Key:</label>
                    <input type="password" id="api-key" placeholder="Enter your API key" />
                </div>
            </div>

            <div class="section">
                <h2>🚀 Start OAuth Flow</h2>
                <p>Click the button below to start the Google OAuth authentication process. This will get you a fresh token.</p>
                <button onclick="startOAuth()">Start Google OAuth</button>
                <div id="oauth-instructions" style="display:none;">
                    <p><strong>Instructions:</strong></p>
                    <ol>
                        <li>Click the authorization link that appears below</li>
                        <li>Sign in to your Google account</li>
                        <li>Grant the requested permissions</li>
                        <li>You'll be redirected back and see a success message</li>
                    </ol>
                </div>
            </div>

            <div class="section">
                <h2>🔧 Troubleshooting</h2>
                <h3>Common Issues:</h3>
                <ul>
                    <li><strong>"Token has been expired or revoked"</strong> - Your refresh token is no longer valid. Use the OAuth flow above to get a new one.</li>
                    <li><strong>"No refresh_token stored"</strong> - The initial OAuth didn't include offline access. Re-authenticate above.</li>
                    <li><strong>"invalid_grant"</strong> - Token was revoked in your Google account or expired (6 months of inactivity). Re-authenticate above.</li>
                </ul>
                
                <h3>Prevention Tips:</h3>
                <ul>
                    <li>Use your application at least once every 6 months to prevent refresh token expiry</li>
                    <li>Don't revoke access in your Google account unless you want to reset tokens</li>
                    <li>The app automatically ensures 'offline' access and 'consent' prompt for reliable refresh tokens</li>
                </ul>
            </div>
        </div>

        <script>
            let apiKey = '';
            
            function getApiKey() {{
                apiKey = document.getElementById('api-key').value;
                if (!apiKey) {{
                    alert('Please enter your API key first');
                    return false;
                }}
                return true;
            }}

            async function checkStatus() {{
                if (!getApiKey()) return;
                
                const statusDiv = document.getElementById('status-display');
                statusDiv.innerHTML = 'Checking...';
                
                try {{
                    const response = await fetch('/oauth/google/status', {{
                        headers: {{ 'X-API-Key': apiKey }}
                    }});
                    
                    if (!response.ok) {{
                        throw new Error(`HTTP ${{response.status}}: ${{await response.text()}}`);
                    }}
                    
                    const status = await response.json();
                    let cssClass = 'ok';
                    if (status.status === 'no_token' || status.status === 'no_refresh_token') {{
                        cssClass = 'error';
                    }} else if (status.status === 'expired' || status.status === 'expired_no_access') {{
                        cssClass = 'warning';
                    }}
                    
                    statusDiv.innerHTML = `
                        <div class="status ${{cssClass}}">
                            <strong>${{status.status.toUpperCase()}}</strong>: ${{status.message}}
                        </div>
                        <div class="code">
                            <strong>Details:</strong><br>
                            Has Access Token: ${{status.has_access_token}}<br>
                            Has Refresh Token: ${{status.has_refresh_token}}<br>
                            Expires In: ${{status.expires_in_seconds}} seconds<br>
                            Scope: ${{status.scope || 'None'}}
                        </div>
                    `;
                }} catch (error) {{
                    statusDiv.innerHTML = `<div class="status error">Error: ${{error.message}}</div>`;
                }}
            }}

            async function startOAuth() {{
                if (!getApiKey()) return;
                
                try {{
                    const redirectUri = `${{window.location.origin}}/oauth/google/callback`;
                    const response = await fetch(`/oauth/google/start?redirect_uri=${{encodeURIComponent(redirectUri)}}`, {{
                        headers: {{ 'X-API-Key': apiKey }}
                    }});
                    
                    if (!response.ok) {{
                        throw new Error(`HTTP ${{response.status}}: ${{await response.text()}}`);
                    }}
                    
                    const data = await response.json();
                    document.getElementById('oauth-instructions').style.display = 'block';
                    document.getElementById('oauth-instructions').innerHTML += `
                        <div style="margin: 20px 0;">
                            <strong>🔗 <a href="${{data.authorize_url}}" target="_blank">Click here to authorize</a></strong>
                        </div>
                        <div class="status warning">
                            <strong>Note:</strong> After authorizing, you'll be redirected back to this domain. 
                            The callback will show a JSON response with "status": "ok" if successful.
                        </div>
                    `;
                }} catch (error) {{
                    alert(`Error starting OAuth: ${{error.message}}`);
                }}
            }}

            // Auto-check status on page load if API key is provided
            window.addEventListener('load', function() {{
                const apiKeyInput = document.getElementById('api-key');
                apiKeyInput.addEventListener('change', function() {{
                    if (this.value) {{
                        checkStatus();
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """
    return html_content