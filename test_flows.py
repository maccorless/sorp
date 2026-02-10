#!/usr/bin/env python3
"""
SARP API Testing Script - Tests all authentication flows
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_result(test_name, success, details=""):
    status = "✓ PASS" if success else "✗ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"    {details}")

# Test Flow 1: Accreditation Registration and Contact Management
print_section("Test Flow 1: Accreditation Registration")

# 1. Register with accreditation
device_id = f"test-device-{datetime.now().timestamp()}"
response = requests.post(f"{BASE_URL}/auth/accreditation", json={
    "accreditation_number": "87654321",
    "accreditation_cvv": "5678",
    "device_id": device_id
})
data = response.json()
print_result("Register with accreditation", data.get('success'),
             f"User ID: {data.get('user_id')}, Session: {data.get('session_token')[:20]}...")

session_token = data.get('session_token')
user_id = data.get('user_id')

# 2. Check authentication
response = requests.get(f"{BASE_URL}/auth/check",
                       headers={"Authorization": f"Bearer {session_token}"})
data = response.json()
print_result("Check authentication", data.get('authenticated'),
             f"Authenticated as user {data.get('user_id')}")

# 3. Add first email
response = requests.post(f"{BASE_URL}/contacts",
                        headers={"Authorization": f"Bearer {session_token}"},
                        json={"contact_type": "email", "contact_value": "user1@example.com"})
data = response.json()
print_result("Add first email", data.get('success'),
             f"Contact ID: {data.get('contact_id')}")

# 4. Add second email (should trigger notification)
print("\n(Check server console for notification message)")
response = requests.post(f"{BASE_URL}/contacts",
                        headers={"Authorization": f"Bearer {session_token}"},
                        json={"contact_type": "email", "contact_value": "user2@example.com"})
data = response.json()
print_result("Add second email", data.get('success'),
             f"Contact ID: {data.get('contact_id')}")

# 5. Try to add third email (should fail)
response = requests.post(f"{BASE_URL}/contacts",
                        headers={"Authorization": f"Bearer {session_token}"},
                        json={"contact_type": "email", "contact_value": "user3@example.com"})
data = response.json()
print_result("Reject third email", not data.get('success'),
             f"Error: {data.get('error')}")

# 6. Add phone numbers
response = requests.post(f"{BASE_URL}/contacts",
                        headers={"Authorization": f"Bearer {session_token}"},
                        json={"contact_type": "phone", "contact_value": "+15551234567"})
data = response.json()
print_result("Add first phone", data.get('success'),
             f"Contact ID: {data.get('contact_id')}")

response = requests.post(f"{BASE_URL}/contacts",
                        headers={"Authorization": f"Bearer {session_token}"},
                        json={"contact_type": "phone", "contact_value": "+15559876543"})
data = response.json()
print_result("Add second phone", data.get('success'),
             f"Contact ID: {data.get('contact_id')}")

# 7. Get all contacts
response = requests.get(f"{BASE_URL}/contacts",
                       headers={"Authorization": f"Bearer {session_token}"})
data = response.json()
contacts = data.get('contacts', [])
print_result("Get contacts", len(contacts) == 4,
             f"Found {len(contacts)} contacts (2 emails, 2 phones)")

# Test Flow 2: OTP Authentication
print_section("Test Flow 2: OTP Authentication")

# 1. Request OTP for registered email
response = requests.post(f"{BASE_URL}/auth/request-otp", json={
    "contact_type": "email",
    "contact_value": "user1@example.com"
})
data = response.json()
otp_code = data.get('otp_code')
print_result("Request OTP", data.get('success'),
             f"OTP Code: {otp_code}")

# 2. Verify OTP with new device
new_device_id = f"test-device-otp-{datetime.now().timestamp()}"
response = requests.post(f"{BASE_URL}/auth/verify-otp", json={
    "contact_value": "user1@example.com",
    "otp_code": otp_code,
    "device_id": new_device_id
})
data = response.json()
otp_session = data.get('session_token')
print_result("Verify OTP and create session", data.get('success'),
             f"New device session: {otp_session[:20] if otp_session else 'None'}...")

# 3. Check authentication with OTP session
response = requests.get(f"{BASE_URL}/auth/check",
                       headers={"Authorization": f"Bearer {otp_session}"})
data = response.json()
print_result("Authenticate with OTP session", data.get('authenticated'),
             f"User ID: {data.get('user_id')}")

# Test Flow 3: Token Authentication
print_section("Test Flow 3: Token Authentication")

# 1. Register with token
token_device_id = f"test-device-token-{datetime.now().timestamp()}"
response = requests.post(f"{BASE_URL}/auth/token", json={
    "token": "9999-8888-7777-6666",
    "device_id": token_device_id
})
data = response.json()
token_session = data.get('session_token')
print_result("Register with token", data.get('success'),
             f"User ID: {data.get('user_id')}, Session: {token_session[:20] if token_session else 'None'}...")

# Test Flow 4: Format Validation
print_section("Test Flow 4: Format Validation")

# 1. Invalid accreditation number (too short)
response = requests.post(f"{BASE_URL}/auth/accreditation", json={
    "accreditation_number": "1234567",
    "accreditation_cvv": "1234",
    "device_id": "test-invalid"
})
data = response.json()
print_result("Reject invalid accreditation (7 digits)", not data.get('success'),
             f"Error: {data.get('error')}")

# 2. Invalid CVV (too long)
response = requests.post(f"{BASE_URL}/auth/accreditation", json={
    "accreditation_number": "12345678",
    "accreditation_cvv": "12345",
    "device_id": "test-invalid"
})
data = response.json()
print_result("Reject invalid CVV (5 digits)", not data.get('success'),
             f"Error: {data.get('error')}")

# 3. Invalid token format
response = requests.post(f"{BASE_URL}/auth/token", json={
    "token": "1111-2222-3333",
    "device_id": "test-invalid"
})
data = response.json()
print_result("Reject invalid token format", not data.get('success'),
             f"Error: {data.get('error')}")

# 4. Invalid email format
response = requests.post(f"{BASE_URL}/contacts",
                        headers={"Authorization": f"Bearer {session_token}"},
                        json={"contact_type": "email", "contact_value": "not-an-email"})
data = response.json()
print_result("Reject invalid email", not data.get('success'),
             f"Error: {data.get('error')}")

# Test Flow 5: Logout
print_section("Test Flow 5: Logout")

# 1. Logout
response = requests.post(f"{BASE_URL}/auth/logout",
                        headers={"Authorization": f"Bearer {session_token}"})
data = response.json()
print_result("Logout", data.get('success'))

# 2. Check authentication after logout (should fail)
response = requests.get(f"{BASE_URL}/auth/check",
                       headers={"Authorization": f"Bearer {session_token}"})
print_result("Verify session removed", response.status_code == 401,
             "Session no longer valid")

# Admin View
print_section("Admin View - All Registrations")

response = requests.get(f"{BASE_URL}/admin/registrations")
data = response.json()
users = data.get('users', [])
print(f"Total registered users: {len(users)}\n")

for user in users:
    print(f"User ID: {user['id']}")
    if user['accreditation_number']:
        print(f"  Accreditation: {user['accreditation_number']}")
    if user['token']:
        print(f"  Token: {user['token']}")
    print(f"  Active Devices: {user['device_count']}")
    print(f"  Contacts: {len(user['contacts'])}")
    for contact in user['contacts']:
        primary = " (Primary)" if contact['is_primary'] else ""
        print(f"    - {contact['contact_type']}: {contact['contact_value']}{primary}")
    print(f"  Registered: {user['created_at']}")
    print()

print_section("Test Summary")
print("All tests completed! Check results above.")
print("\nView the application in your browser:")
print("  Main Login:  http://localhost:5000/")
print("  MediaZone:   http://localhost:5000/mediazone/index.html")
print("  Admin View:  http://localhost:5000/frontend/admin.html")
print("  Account Mgr: http://localhost:5000/frontend/account.html")
print()
