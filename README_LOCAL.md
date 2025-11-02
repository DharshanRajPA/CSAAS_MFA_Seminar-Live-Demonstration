# MFA Demo - Multi-Factor Authentication System

A complete local demonstration of Multi-Factor Authentication (MFA) with TOTP (Google Authenticator) and Email OTP fallback.

## 🚀 Quick Start

### Windows
```powershell
.\start_local.ps1
```

### Linux/Mac
```bash
./start_local.sh
```

The server will start at **http://localhost:5000**

## 📋 Features

- ✅ Email + Password Registration & Login
- ✅ TOTP-based MFA (Google Authenticator compatible)
- ✅ Email OTP fallback for users without TOTP
- ✅ Session management with JWT tokens
- ✅ SQLite database (no external dependencies)
- ✅ Modern responsive web interface
- ✅ Complete API documentation

## 🛠️ Manual Testing with cURL

### 1. Register a User
```bash
curl -s -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"Password123!"}'
```

**Expected Response:**
```json
{"success": true, "user_id": 1}
```

### 2. Login (No MFA Yet)
```bash
curl -s -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"Password123!"}'
```

**Expected Response:**
```json
{"token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}
```

### 3. Enable TOTP MFA
```bash
# First, get a login token, then enable MFA
TOKEN="your_jwt_token_here"

curl -s -X POST http://localhost:5000/api/mfa/enable \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}'
```

**Expected Response:**
```json
{
  "qr_png_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "secret": "JBSWY3DPEHPK3PXP"
}
```

**Note:** The QR code is base64-encoded PNG. You can decode and display it, or use the secret to manually add to your authenticator app.

### 4. Login with MFA Enabled
```bash
# Initial login returns MFA requirement
curl -s -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"Password123!"}'
```

**Expected Response:**
```json
{
  "mfa_required": true,
  "temp_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 5. Verify TOTP Code
```bash
# Use the 6-digit code from your authenticator app
TEMP_TOKEN="your_temp_token_here"
TOTP_CODE="123456"

curl -s -X POST http://localhost:5000/api/mfa/totp/verify \
  -H "Content-Type: application/json" \
  -d "{\"temp_token\":\"$TEMP_TOKEN\",\"totp_code\":\"$TOTP_CODE\"}"
```

**Expected Response:**
```json
{"token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}
```

### 6. Email OTP Fallback
```bash
# Send OTP to email (prints to server console in demo)
curl -s -X POST http://localhost:5000/api/mfa/email/send_otp \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com"}'
```

**Expected Response:**
```json
{"success": true, "message": "OTP sent to console for demo"}
```

**Note:** Check the server console for the OTP code.

```bash
# Verify email OTP
EMAIL_OTP="123456"
TEMP_TOKEN="your_temp_token_here"

curl -s -X POST http://localhost:5000/api/mfa/email/verify \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"demo@example.com\",\"otp\":\"$EMAIL_OTP\",\"temp_token\":\"$TEMP_TOKEN\"}"
```

### 7. Access Protected Resource
```bash
# Get user profile (requires valid JWT)
JWT_TOKEN="your_final_jwt_token_here"

curl -s -H "Authorization: Bearer $JWT_TOKEN" http://localhost:5000/api/profile
```

**Expected Response:**
```json
{
  "user_id": 1,
  "email": "demo@example.com",
  "mfa_enabled": true,
  "created_at": "2024-01-01 12:00:00"
}
```

## 🎭 Demo Script for Live Presentation

### Step 1: Registration & Basic Login
1. Open http://localhost:5000 in browser
2. Register a new user (demo@example.com)
3. Login and show successful authentication
4. **Show:** Server console logs for registration and login

### Step 2: Enable MFA
1. Click "Enable MFA" button
2. **Show:** QR code displayed on screen
3. **Show:** Secret key printed in server console
4. Scan QR with Google Authenticator or Authy
5. **Show:** MFA status changed to "Enabled"

### Step 3: Login with MFA
1. Logout and login again
2. **Show:** "MFA Required" screen appears
3. Enter 6-digit code from authenticator app
4. **Show:** Successful login to dashboard
5. **Show:** Profile shows MFA is enabled

### Step 4: Email OTP Fallback
1. Create another user or disable MFA for current user
2. Login and choose "Use Email OTP Instead"
3. **Show:** OTP printed in server console
4. Enter OTP code
5. **Show:** Successful login via email OTP

## 🔧 Technical Details

### Database Schema
```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    totp_secret TEXT,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OTPs table
CREATE TABLE otps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    otp_hash TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    type TEXT DEFAULT 'email',
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/register` | Register new user | No |
| POST | `/api/login` | Login user | No |
| POST | `/api/mfa/enable` | Enable TOTP MFA | Yes |
| POST | `/api/mfa/totp/verify` | Verify TOTP code | No (temp token) |
| POST | `/api/mfa/email/send_otp` | Send email OTP | No |
| POST | `/api/mfa/email/verify` | Verify email OTP | No (temp token) |
| GET | `/api/profile` | Get user profile | Yes |

### Security Features
- ✅ Password hashing with bcrypt
- ✅ JWT tokens with 15-minute expiry
- ✅ TOTP with 1-step clock drift tolerance
- ✅ Email OTP with 5-minute expiry
- ✅ SQL injection protection
- ✅ CORS enabled for frontend

## 🐛 Troubleshooting

### Common Issues

1. **"Python not found"**
   - Install Python 3.7+ from https://python.org
   - Ensure Python is in your PATH

2. **"Module not found" errors**
   - Run: `pip install -r backend-minimal-flask/requirements.txt`
   - Ensure virtual environment is activated

3. **"Database is locked"**
   - Stop the server (Ctrl+C)
   - Delete `auth_demo.db` file
   - Restart the server

4. **"Port 5000 already in use"**
   - Change port in `server.py` (line 95)
   - Or kill process using port 5000

### Production Deployment Notes

- Change `JWT_SECRET` in `auth_core.py` to a secure random string
- Implement real SMTP for email OTP (replace console printing)
- Add rate limiting for login attempts
- Use HTTPS in production
- Implement proper logging
- Add database backups

## 📁 Project Structure

```
MFA_Demo_1/
├── backend-minimal-flask/
│   ├── auth_core.py          # Core authentication logic
│   ├── server.py             # Flask server with API endpoints
│   ├── db_init.py            # Database initialization
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── index.html            # Main web interface
│   └── app.js                # Frontend JavaScript
├── start_local.sh            # Linux/Mac start script
├── start_local.ps1           # Windows start script
├── README_LOCAL.md           # This documentation
└── auth_demo.db              # SQLite database (created on first run)
```

## 🎯 Success Criteria

✅ **Server starts successfully** with `./start_local.sh` or `.\start_local.ps1`  
✅ **Registration works** - can create new users  
✅ **Login works** - can authenticate users  
✅ **MFA setup works** - can enable TOTP and display QR code  
✅ **MFA login works** - requires TOTP code for login  
✅ **Email OTP works** - fallback authentication method  
✅ **Protected resources work** - can access `/api/profile` with valid token  
✅ **All cURL commands work** - manual testing passes  
✅ **No CI/CD artifacts** - clean, minimal codebase  

## 🚀 Ready to Demo!

Your MFA demo is now ready for presentation. The system demonstrates:
- Modern authentication flows
- Multi-factor security
- User-friendly interfaces
- Robust error handling
- Complete API coverage

**Happy Demo-ing! 🎉**
