# Device Limits Feature

## Overview

SARP implements a tiered device access system to encourage users to link their email addresses:

- **Without Email**: Maximum 3 devices
- **With Email**: Unlimited devices

## Rationale

This feature:
1. Encourages users to add email addresses for account recovery
2. Enables OTP-based authentication
3. Provides flexibility for users with many devices
4. Creates a natural upgrade path

## How It Works

### Without Email

When a user registers with **only** accreditation or token (no email contact):
- They can authenticate on up to **3 different devices**
- Attempting to add a 4th device returns an error:
  ```
  "Device limit reached (3 devices max). Add an email address to your account for unlimited devices."
  ```

### With Email

Once a user adds **any email address** to their account:
- The 3-device limit is immediately removed
- They can authenticate on **unlimited devices**
- This applies retroactively to existing accounts

### OTP Authentication

Users who authenticate via OTP:
- Must have a registered email/phone contact
- Automatically have unlimited device access
- The 3-device limit never applies to them

## Technical Implementation

### Database Functions

**`count_active_devices(user_id)`**
- Counts non-expired devices for a user
- Only counts devices where `expires_at > current_time`

**`user_has_email(user_id)`**
- Checks if user has any email contacts
- Returns `True` if count > 0

**`create_device(device_id, user_id)`**
- Modified to return tuple: `(device_id, error_message)`
- Checks device limit before creating new device
- Bypasses limit check if user has email
- Allows existing devices to refresh (no limit check)

### API Changes

All authentication endpoints now handle the tuple return:
```python
session_token, error = db.create_device(device_id, user_id)

if error:
    return jsonify({'success': False, 'error': error}), 403
```

Endpoints affected:
- `POST /api/auth/accreditation`
- `POST /api/auth/token`
- `POST /api/auth/verify-otp`

## User Experience

### Login Page

An info box displays the device limits:
```
📱 Device Limits:
• Without email: Maximum 3 devices
• With email linked: Unlimited devices

Add an email address in Account Management for unlimited device access.
```

### Account Management Page

A benefit callout in the email section:
```
✨ Benefit: Adding an email unlocks unlimited device access!
Without an email, you're limited to 3 devices.
```

### Error Message

When limit is reached:
```json
{
  "success": false,
  "error": "Device limit reached (3 devices max). Add an email address to your account for unlimited devices."
}
```

## Test Cases

### Test 1: Enforce 3-Device Limit
```
1. Create user with accreditation (no email)
2. Login device 1 → ✓ Success
3. Login device 2 → ✓ Success
4. Login device 3 → ✓ Success
5. Login device 4 → ✗ Rejected (limit reached)
```

### Test 2: Email Unlocks Unlimited
```
1. User has 3 devices (at limit)
2. Add email to account → ✓ Success
3. Login device 4 → ✓ Success (now allowed)
4. Login device 5 → ✓ Success
5. Login device 6 → ✓ Success (unlimited)
```

### Test 3: Token Authentication
```
1. Create user with token (no email)
2. Login device 1, 2, 3 → ✓ All succeed
3. Login device 4 → ✗ Rejected
```

### Test 4: OTP Bypass
```
1. User registers with accreditation
2. Adds email: user@example.com
3. Logs in via OTP on device 1 → ✓ Success
4. Logs in via OTP on device 4, 5, 6... → ✓ All succeed
   (No limit because email is required for OTP)
```

### Test 5: Existing Device Refresh
```
1. User has 3 devices (at limit)
2. Device 1 logs in again → ✓ Success
   (Refreshes existing device, doesn't count as new)
```

## Code References

### backend/database.py
- Lines 153-159: `count_active_devices()`
- Lines 161-170: `user_has_email()`
- Lines 115-147: `create_device()` with limit check

### backend/app.py
- Lines 45-49: Accreditation endpoint error handling
- Lines 80-84: Token endpoint error handling
- Lines 146-150: OTP verify endpoint error handling

### frontend/index.html
- Lines 88-95: Device limits info box

### frontend/account.html
- Lines 22-25: Email benefit callout

## Benefits

**For Users:**
- Clear upgrade path (3 → unlimited)
- Immediate benefit when adding email
- No loss of existing access

**For System:**
- Encourages email registration
- Enables account recovery
- Supports OTP authentication
- Reduces anonymous accounts

## Monitoring

Check device counts in Admin View:
- Users with 3 active devices (likely at limit)
- Users with email but 0-2 devices (underutilizing)
- Users with many devices (email linked)

## Future Enhancements

1. **Notification**: Alert users at device 2 about upcoming limit
2. **Grace Period**: Allow 4th device with warning
3. **Phone Alternative**: Unlimited devices with email OR phone
4. **Tiered Limits**: Different limits for different account types
5. **Analytics**: Track conversion rate (3-device → email added)

## Summary

✅ Users without email: 3-device maximum
✅ Users with email: Unlimited devices
✅ Encourages email registration
✅ Seamless upgrade experience
✅ OTP users automatically unlimited
✅ Existing devices can refresh without limit
✅ Clear error messages guide users

The feature is production-ready and fully tested.
