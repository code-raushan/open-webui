# External Authentication Integration

This document describes the integration of external authentication with the OpenWebUI codebase, allowing users to authenticate via an external server that supports OTP and Google authentication.

## Overview

The external authentication integration allows OpenWebUI to proxy authentication requests to an external server (https://api.euron.one/api/v1/auth) that handles:
- OTP-based authentication (send OTP, verify OTP)
- Google OAuth authentication

## Database Changes

### User Model Updates

The `User` model has been extended with the following fields:

```python
# External authentication fields
external_user_id = Column(String, nullable=True, unique=True)
phone = Column(String, nullable=True, unique=True)
auth_provider = Column(String, nullable=True)  # 'CREDENTIALS', 'GOOGLE', 'OTP'
```

### Auth Model Updates

The `Auth` model has been extended with the following fields:

```python
# External authentication fields
external_user_id = Column(String, nullable=True, unique=True)
phone = Column(String, nullable=True, unique=True)
auth_provider = Column(String, nullable=True)
```

## Configuration

Add the following environment variables to enable external authentication:

```bash
# Enable external authentication
ENABLE_EXTERNAL_AUTH=true

# External auth server configuration
EXTERNAL_AUTH_BASE_URL=https://api.euron.one/api/v1/auth
EXTERNAL_AUTH_TIMEOUT=30

# Enable specific authentication methods
EXTERNAL_AUTH_ENABLE_OTP=true
EXTERNAL_AUTH_ENABLE_GOOGLE=true
```

## API Endpoints

### Send OTP
```
POST /api/auth/external/send-otp
```

**Request Body:**
```json
{
  "phone": "+1234567890",
  "hash": "optional_hash"
}
```

**Query Parameters:**
- `affiliate_code` (optional): Referral code

**Response:**
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "session": "session_token"
}
```

### Verify OTP
```
POST /api/auth/external/verify-otp
```

**Request Body:**
```json
{
  "phone": "+1234567890",
  "code": "123456",
  "session": "session_token"
}
```

**Query Parameters:**
- `affiliate_code` (optional): Referral code

**Response:**
```json
{
  "token": "jwt_token",
  "token_type": "Bearer",
  "expires_at": 1234567890,
  "id": "user_id",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "profile_image_url": "/user.png",
  "permissions": {}
}
```

### Google Authentication
```
POST /api/auth/external/google
```

**Request Body:**
```json
{
  "googleToken": "google_id_token"
}
```

**Query Parameters:**
- `affiliate_code` (optional): Referral code

**Response:**
```json
{
  "token": "jwt_token",
  "token_type": "Bearer",
  "expires_at": 1234567890,
  "id": "user_id",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "profile_image_url": "/user.png",
  "permissions": {}
}
```

## Implementation Details

### User Creation Flow

1. **External Authentication**: User authenticates with external server
2. **User Lookup**: Check if user exists by:
   - `external_user_id` (primary)
   - `email` (fallback)
   - `phone` (fallback)
3. **User Creation**: If user doesn't exist, create new user with:
   - External user ID from main server
   - User information from external response
   - Default role (admin if first user, otherwise configured default)
4. **JWT Token**: Generate JWT token for OpenWebUI session
5. **Cookie Setting**: Set secure HTTP-only cookie

### User Information Mapping

The external server user model is mapped to OpenWebUI user model:

| External Field | OpenWebUI Field | Notes |
|----------------|-----------------|-------|
| `id` | `external_user_id` | Primary identifier from external server |
| `firstName` + `lastName` | `name` | Combined full name |
| `email` | `email` | User email address |
| `phone` | `phone` | Phone number |
| `profilePic` | `profile_image_url` | Profile picture URL |
| `authProvider` | `auth_provider` | Authentication method used |

### Security Considerations

1. **HTTPS Only**: All external API calls use HTTPS
2. **Timeout Protection**: Configurable timeout for external API calls
3. **Error Handling**: Comprehensive error handling for external API failures
4. **User Validation**: Multiple fallback methods for user identification
5. **Secure Cookies**: HTTP-only, secure cookies for session management

## Migration

To apply the database changes, run:

```bash
cd backend
alembic revision --autogenerate -m "add external authentication fields"
alembic upgrade head
```

## Testing

Run the test script to verify the implementation:

```bash
cd backend
python test_external_auth.py
```

## Usage Examples

### Frontend Integration

```javascript
// Send OTP
const sendOtpResponse = await fetch('/api/auth/external/send-otp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ phone: '+1234567890' })
});

// Verify OTP
const verifyOtpResponse = await fetch('/api/auth/external/verify-otp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone: '+1234567890',
    code: '123456',
    session: 'session_token'
  })
});

// Google Authentication
const googleAuthResponse = await fetch('/api/auth/external/google', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ googleToken: 'google_id_token' })
});
```

### cURL Examples

```bash
# Send OTP
curl -X POST http://localhost:8080/api/auth/external/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890"}'

# Verify OTP
curl -X POST http://localhost:8080/api/auth/external/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890", "code": "123456", "session": "session_token"}'

# Google Authentication
curl -X POST http://localhost:8080/api/auth/external/google \
  -H "Content-Type: application/json" \
  -d '{"googleToken": "google_id_token"}'
```

## Troubleshooting

### Common Issues

1. **External server not reachable**: Check network connectivity and external server status
2. **Timeout errors**: Increase `EXTERNAL_AUTH_TIMEOUT` value
3. **Authentication disabled**: Ensure `ENABLE_EXTERNAL_AUTH=true`
4. **Method not enabled**: Check `EXTERNAL_AUTH_ENABLE_OTP` and `EXTERNAL_AUTH_ENABLE_GOOGLE`

### Logs

Check the application logs for detailed error messages:

```bash
tail -f logs/app.log | grep -i "external"
```

## Future Enhancements

1. **Rate Limiting**: Add rate limiting for external auth endpoints
2. **Caching**: Implement caching for external user data
3. **Webhook Support**: Add webhooks for user updates from external server
4. **Multi-tenant Support**: Support multiple external auth providers
5. **Audit Logging**: Enhanced audit logging for external authentication events 