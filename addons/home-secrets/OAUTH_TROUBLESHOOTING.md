# OAuth Token Management & Troubleshooting

## Overview

This addon uses Google OAuth with refresh tokens for persistent access. The most common issue is "Token has been expired or revoked" which occurs when refresh tokens become invalid.

## Quick Fix

1. Navigate to `/oauth` in your browser
2. Enter your API key
3. Click "Start Google OAuth"
4. Follow the authorization link
5. Complete the Google OAuth flow

## Common Error Messages & Solutions

### "Token has been expired or revoked"

**Cause:** Your refresh token is no longer valid. This happens when:
- Refresh token expired (6+ months of inactivity)
- User revoked access in Google account
- Google invalidated the token for security reasons

**Solution:** Re-authenticate using `/oauth` route

### "No refresh_token stored"

**Cause:** The initial OAuth flow didn't properly store a refresh token.

**Solution:** Re-authenticate using `/oauth` route (ensures proper offline access)

### "invalid_grant" error

**Cause:** Refresh token was revoked or expired.

**Solution:** The system automatically clears bad tokens. Re-authenticate using `/oauth` route.

## Prevention Tips

1. **Use your application regularly** - Access it at least once every 6 months to prevent refresh token expiry
2. **Don't revoke access** - Avoid revoking access in your Google account settings unless you intend to reset tokens
3. **Monitor token status** - Check `/oauth/google/status` endpoint periodically
4. **Use the web UI** - The `/oauth` route provides an easy way to manage tokens

## API Endpoints for Token Management

### Check Token Status
```
GET /oauth/google/status
Headers: X-API-Key: your-api-key
```

### Get Fresh Access Token
```
GET /oauth/google/token
Headers: X-API-Key: your-api-key
```

### Delete Corrupted Tokens
```
DELETE /oauth/google/token
Headers: X-API-Key: your-api-key
```

### Start OAuth Flow (Programmatic)
```
GET /oauth/google/start?redirect_uri=https://your-domain.com/callback
Headers: X-API-Key: your-api-key
```

## OAuth Flow Details

The system automatically:
- Sets `access_type=offline` to ensure refresh tokens
- Sets `prompt=consent` to force token regeneration
- Stores both access and refresh tokens securely
- Handles token refresh automatically
- Clears invalid tokens when refresh fails

## Debugging

1. Check current status: Visit `/oauth` and click "Refresh Status"
2. Review error messages in the API responses
3. Check Home Assistant logs for detailed error information
4. Use the web UI at `/oauth` for guided troubleshooting

## Security Notes

- Tokens are stored in `/data/hs/google_tokens.json`
- All endpoints require API key authentication
- Refresh tokens are preserved during access token refresh
- Invalid tokens are automatically cleared to prevent repeated failures