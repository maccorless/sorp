# SARP (Son of Access Request Portal) - Prototype

A prototype Single Sign-On (SSO) demonstration application showcasing simplified authentication flows.

## Features

- **Three Authentication Methods:**
  - Accreditation Number + CVV (8 digits + 4 digits)
  - Third-party Token (####-####-####-####)
  - Email/Phone OTP (for registered contacts)

- **90-Day Device Authentication:**
  - Stay logged in for 90 days on trusted devices
  - Automatic session management

- **Device Limits:**
  - **Without email**: Maximum 3 devices per account
  - **With email linked**: Unlimited devices
  - Encourages users to add email for better access

- **Contact Management:**
  - Link up to 2 email addresses
  - Link up to 2 phone numbers
  - Notifications when second contact is added

- **Demo Features:**
  - OTP codes displayed in browser (for testing)
  - Admin view to see all registrations
  - Simple, clean UI design

## Technology Stack

- **Backend:** Python Flask
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Database:** SQLite (file-based)
- **Dependencies:** Flask, Flask-CORS

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Navigate to the project directory:
   ```bash
   cd sarp-prototype
   ```

2. Install Python dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Run the Flask application:
   ```bash
   python app.py
   ```

   The server will start on `http://localhost:5000`

4. Open your browser and navigate to:
   - Main Login: `http://localhost:5000/frontend/index.html`
   - MediaZone: `http://localhost:5000/mediazone/index.html`
   - Admin View: `http://localhost:5000/frontend/admin.html`

## Usage Guide

### First-Time Registration

#### Option 1: Accreditation
1. Navigate to `http://localhost:5000/frontend/index.html`
2. Select "Accreditation" tab
3. Enter 8-digit accreditation number (e.g., `12345678`)
4. Enter 4-digit CVV (e.g., `1234`)
5. Click "Sign In"
6. You'll be redirected to MediaZone

#### Option 2: Token
1. Navigate to `http://localhost:5000/frontend/index.html`
2. Select "Token" tab
3. Enter token in format ####-####-####-#### (e.g., `1111-2222-3333-4444`)
4. Click "Sign In"
5. You'll be redirected to MediaZone

### Adding Email/Phone for OTP Login

1. After logging in with accreditation or token
2. Click "Manage Account" in MediaZone
3. Click "Add Email" or "Add Phone"
4. Enter your email/phone and click "Save"
5. Now you can use this contact for OTP login

### Login with Email/Phone OTP

1. Navigate to `http://localhost:5000/frontend/index.html`
2. Select "Email/Phone" tab
3. Enter your registered email or phone
4. Click "Request OTP"
5. The OTP will be displayed in a yellow box (demo mode)
6. Enter the 6-digit OTP code
7. Click "Verify OTP"
8. You'll be redirected to MediaZone

### Device Persistence

- Once logged in, your device remains authenticated for 90 days
- Close and reopen your browser - you'll stay logged in
- Navigate to MediaZone directly without logging in again

### Admin View

- Navigate to `http://localhost:5000/frontend/admin.html`
- View all registered users
- See linked contacts and active devices
- No authentication required (demo only)

## Testing the Application

### Test Case 1: First-Time Registration with Accreditation
```
Accreditation: 12345678
CVV: 1234
Expected: User created, redirected to MediaZone
```

### Test Case 2: First-Time Registration with Token
```
Token: 1111-2222-3333-4444
Expected: User created, redirected to MediaZone
```

### Test Case 3: Add Email Contact
```
1. Log in with accreditation/token
2. Go to Account Management
3. Add email: test@example.com
4. Check admin view - email should appear
```

### Test Case 4: Add Second Contact (Notification)
```
1. Add first email: test1@example.com
2. Add second email: test2@example.com
3. Check browser console - should see notification log
```

### Test Case 5: Login with OTP
```
1. Clear localStorage (simulate new device)
2. Try to access MediaZone - redirected to login
3. Select Email/Phone tab
4. Enter: test@example.com
5. Click Request OTP
6. Copy OTP from yellow display box
7. Enter OTP and verify
Expected: Logged in and redirected to MediaZone
```

### Test Case 6: Contact Limits
```
1. Try adding 3rd email
Expected: Error message "Maximum 2 emails allowed"
```

### Test Case 7: 90-Day Persistence
```
1. Log in successfully
2. Close browser completely
3. Reopen and navigate to MediaZone
Expected: Still authenticated, no redirect
```

### Test Case 8: Device Limits
```
1. Create new user with accreditation (no email)
2. Login from device 1 - Success
3. Login from device 2 - Success
4. Login from device 3 - Success
5. Try to login from device 4 - Error: "Device limit reached"
6. Add email to account
7. Try device 4 again - Success (unlimited devices)
```

## API Endpoints

### Authentication
- `POST /api/auth/accreditation` - Login with accreditation
- `POST /api/auth/token` - Login with token
- `POST /api/auth/request-otp` - Request OTP code
- `POST /api/auth/verify-otp` - Verify OTP and login
- `GET /api/auth/check` - Check if device is authenticated
- `POST /api/auth/logout` - Logout current device

### Contact Management
- `GET /api/contacts` - Get user's contacts
- `POST /api/contacts` - Add new contact
- `DELETE /api/contacts/:id` - Remove contact

### Admin
- `GET /api/admin/registrations` - Get all users and contacts

## Database Schema

The SQLite database (`sarp.db`) is created automatically with these tables:

- **users:** User accounts with accreditation or token
- **contacts:** Email and phone contacts (max 2 each)
- **devices:** Device sessions with 90-day expiry
- **otp_sessions:** Temporary OTP codes (5-minute expiry)

## Important Notes

⚠️ **This is a prototype/demo application:**

- OTP codes are displayed in the browser (not sent via email/SMS)
- No password encryption
- No rate limiting
- Admin view has no authentication
- Session tokens are simple UUIDs (not JWT)
- Not suitable for production use

## Project Structure

```
sarp-prototype/
├── backend/
│   ├── app.py              # Flask application
│   ├── database.py         # Database operations
│   ├── auth.py             # Authentication utilities
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Login/registration page
│   ├── account.html        # Account management page
│   ├── admin.html          # Admin view page
│   ├── styles.css          # Shared styles
│   ├── auth.js             # Authentication logic
│   └── account.js          # Account management logic
├── mediazone/
│   ├── index.html          # MediaZone application
│   ├── mediazone.js        # MediaZone logic
│   └── assets/
│       └── mediazone-screenshot.png
├── sarp.db                 # SQLite database (auto-created)
└── README.md
```

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, edit `backend/app.py` and change:
```python
app.run(debug=True, port=5000)
```
to another port like 5001.

### Database Locked
If you get a "database is locked" error, close all other connections and restart the Flask app.

### CORS Errors
Make sure Flask-CORS is installed:
```bash
pip install Flask-CORS
```

### Clear All Data
To reset the application:
```bash
rm sarp.db
```
The database will be recreated on next startup.

## License

This is a prototype application for demonstration purposes only.
