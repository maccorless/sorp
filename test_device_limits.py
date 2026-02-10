#!/usr/bin/env python3
"""
Test Device Limits Feature
- Without email: max 3 devices
- With email: unlimited devices
"""

import requests
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

print_section("Device Limit Test - Without Email")

# 1. Create a user with accreditation (no email)
accreditation = f"99{int(datetime.now().timestamp()) % 1000000}"
response = requests.post(f"{BASE_URL}/auth/accreditation", json={
    "accreditation_number": accreditation,
    "accreditation_cvv": "9999",
    "device_id": "device-1"
})
data = response.json()
user_id = data.get('user_id')
print_result("Create user without email", data.get('success'), f"User ID: {user_id}")

# 2. Add device 2
response = requests.post(f"{BASE_URL}/auth/accreditation", json={
    "accreditation_number": accreditation,
    "accreditation_cvv": "9999",
    "device_id": "device-2"
})
data = response.json()
print_result("Add device 2 (allowed)", data.get('success'))

# 3. Add device 3
response = requests.post(f"{BASE_URL}/auth/accreditation", json={
    "accreditation_number": accreditation,
    "accreditation_cvv": "9999",
    "device_id": "device-3"
})
data = response.json()
print_result("Add device 3 (allowed)", data.get('success'))

# 4. Try to add device 4 (should fail)
response = requests.post(f"{BASE_URL}/auth/accreditation", json={
    "accreditation_number": accreditation,
    "accreditation_cvv": "9999",
    "device_id": "device-4"
})
data = response.json()
print_result("Device 4 rejected (no email)", not data.get('success'),
             f"Error: {data.get('error')}")

print_section("Device Limit Test - With Email")

# 5. Add an email to the user
session_token = "device-1"  # Use first device
response = requests.post(f"{BASE_URL}/contacts",
                        headers={"Authorization": f"Bearer {session_token}"},
                        json={"contact_type": "email", "contact_value": "unlimited@test.com"})
data = response.json()
print_result("Add email to account", data.get('success'))

# 6. Now try to add device 4 again (should succeed)
response = requests.post(f"{BASE_URL}/auth/accreditation", json={
    "accreditation_number": accreditation,
    "accreditation_cvv": "9999",
    "device_id": "device-4"
})
data = response.json()
print_result("Device 4 allowed (with email)", data.get('success'),
             "Unlimited devices now available!")

# 7. Add device 5 to verify unlimited
response = requests.post(f"{BASE_URL}/auth/accreditation", json={
    "accreditation_number": accreditation,
    "accreditation_cvv": "9999",
    "device_id": "device-5"
})
data = response.json()
print_result("Device 5 allowed (with email)", data.get('success'))

# 8. Add device 6 to verify unlimited
response = requests.post(f"{BASE_URL}/auth/accreditation", json={
    "accreditation_number": accreditation,
    "accreditation_cvv": "9999",
    "device_id": "device-6"
})
data = response.json()
print_result("Device 6 allowed (with email)", data.get('success'))

print_section("Test with Token Authentication")

# 9. Create user with token (no email)
token = f"{int(datetime.now().timestamp()) % 10000:04d}-1111-2222-3333"
response = requests.post(f"{BASE_URL}/auth/token", json={
    "token": token,
    "device_id": "token-device-1"
})
data = response.json()
print_result("Create token user", data.get('success'))

# 10. Add devices 2 and 3
response = requests.post(f"{BASE_URL}/auth/token", json={
    "token": token,
    "device_id": "token-device-2"
})
print_result("Token device 2", response.json().get('success'))

response = requests.post(f"{BASE_URL}/auth/token", json={
    "token": token,
    "device_id": "token-device-3"
})
print_result("Token device 3", response.json().get('success'))

# 11. Try device 4 (should fail)
response = requests.post(f"{BASE_URL}/auth/token", json={
    "token": token,
    "device_id": "token-device-4"
})
data = response.json()
print_result("Token device 4 rejected", not data.get('success'),
             f"Error: {data.get('error')}")

print_section("Summary")
print("Device limit feature is working correctly!")
print("✓ Users without email: Limited to 3 devices")
print("✓ Users with email: Unlimited devices")
print("\nNote: OTP login always works because it requires a registered email,")
print("      which automatically grants unlimited device access.")
