# SARP - Quick Start Guide

## Prerequisites
- Python 3.8+
- pip

## Installation & Setup (30 seconds)

```bash
cd sarp-prototype

# Activate virtual environment (already created)
source venv/bin/activate

# Start the server
python backend/app.py
```

The server will start on **http://localhost:5000**

## Try It Out (5 minutes)

### Option 1: Quick Browser Test

1. **Open:** http://localhost:5000/
2. **Login with Accreditation:**
   - Number: `12345678`
   - CVV: `1234`
3. **Click "Sign In"** → Redirects to MediaZone
4. **Click "Manage Account"** → Add email/phone contacts
5. **Add Email:** `myemail@example.com`
6. **Logout** and try OTP login with that email

### Option 2: Run Automated Tests

```bash
python test_flows.py
```

This will test all authentication flows and display results.

### Option 3: View Admin Dashboard

Open: http://localhost:5000/frontend/admin.html

See all registered users, their contacts, and active devices.

## All Authentication Methods

### 1. Accreditation Number + CVV
- Number: Any 8 digits (e.g., `12345678`)
- CVV: Any 4 digits (e.g., `1234`)

### 2. Third-Party Token
- Format: ####-####-####-#### (e.g., `1111-2222-3333-4444`)
- Auto-formats as you type

### 3. Email/Phone OTP
- First register with accreditation or token
- Add your email/phone in Account Management
- Then use "Email/Phone" tab on login page
- OTP will be displayed in yellow box (demo mode)

## URLs

- **Main Login:** http://localhost:5000/
- **MediaZone:** http://localhost:5000/mediazone/index.html
- **Account Management:** http://localhost:5000/frontend/account.html
- **Admin View:** http://localhost:5000/frontend/admin.html

## Features to Demo

### 90-Day Device Persistence
1. Login with any method
2. Close browser completely
3. Reopen and go to MediaZone
4. You're still logged in! (no redirect)

### Contact Management
1. Login and go to Account Management
2. Add first email → Success
3. Add second email → Success (check server console for notification)
4. Try to add third email → Error (max 2 allowed)

### OTP Flow
1. Register with accreditation: `99999999` / `9999`
2. Add email: `test@demo.com`
3. Logout
4. Select "Email/Phone" tab
5. Enter email: `test@demo.com`
6. Click "Request OTP"
7. OTP appears in yellow box
8. Enter OTP and verify
9. Logged in with new device!

### Device Limits
1. Create account with accreditation (no email)
2. Login from 3 different "devices" (use different device IDs)
3. Try 4th device → Error: "Device limit reached"
4. Add email to account
5. Try 4th device again → Success! (unlimited devices)

**Key Point:** Adding an email unlocks unlimited device access!

### Admin View
- See all users
- View their contacts
- Check active device count
- Auto-refreshes every 10 seconds

## Testing

Run comprehensive tests:
```bash
python test_flows.py
```

Tests include:
- ✅ All 3 authentication methods
- ✅ Contact management (add/remove/limits)
- ✅ Device limits (3 without email, unlimited with email)
- ✅ OTP generation and verification
- ✅ Format validation
- ✅ Device persistence
- ✅ Logout functionality

Test device limits:
```bash
python test_device_limits.py
```

## Stopping the Server

Press `CTRL+C` in the terminal running the Flask app.

## Reset Database

To start fresh:
```bash
rm sarp.db
```

The database will be recreated automatically when you restart the server.

## Troubleshooting

**Port 5000 in use?**
Edit `backend/app.py`, line 278:
```python
app.run(debug=True, port=5001)  # Change to 5001
```

**Can't access from browser?**
Make sure Flask server is running and you see:
```
* Running on http://127.0.0.1:5000
```

**OTP not working?**
Make sure you've added the email/phone to your account first using Account Management after logging in with accreditation or token.

## Next Steps

- Read `README.md` for detailed documentation
- Check `VERIFICATION.md` for test results and implementation details
- Explore the code in `backend/` and `frontend/` directories
