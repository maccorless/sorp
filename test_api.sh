#!/bin/bash

# SARP API Testing Script

BASE_URL="http://localhost:5000/api"
echo "================================"
echo "SARP API Testing"
echo "================================"
echo ""

# Test 1: Register with Accreditation
echo "Test 1: Register with Accreditation"
echo "-----------------------------------"
DEVICE_ID="test-device-$(date +%s)"
RESPONSE=$(curl -s -X POST "$BASE_URL/auth/accreditation" \
  -H "Content-Type: application/json" \
  -d "{\"accreditation_number\":\"12345678\",\"accreditation_cvv\":\"1234\",\"device_id\":\"$DEVICE_ID\"}")
echo "Response: $RESPONSE"
SESSION_TOKEN=$(echo $RESPONSE | grep -o '"session_token":"[^"]*"' | cut -d'"' -f4)
USER_ID=$(echo $RESPONSE | grep -o '"user_id":[0-9]*' | cut -d':' -f2)
echo "Session Token: $SESSION_TOKEN"
echo "User ID: $USER_ID"
echo ""

# Test 2: Check Authentication
echo "Test 2: Check Authentication"
echo "-----------------------------------"
curl -s -X GET "$BASE_URL/auth/check" \
  -H "Authorization: Bearer $SESSION_TOKEN"
echo ""
echo ""

# Test 3: Add Email Contact
echo "Test 3: Add Email Contact"
echo "-----------------------------------"
curl -s -X POST "$BASE_URL/contacts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SESSION_TOKEN" \
  -d "{\"contact_type\":\"email\",\"contact_value\":\"test@example.com\"}"
echo ""
echo ""

# Test 4: Add Phone Contact
echo "Test 4: Add Phone Contact"
echo "-----------------------------------"
curl -s -X POST "$BASE_URL/contacts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SESSION_TOKEN" \
  -d "{\"contact_type\":\"phone\",\"contact_value\":\"+1234567890\"}"
echo ""
echo ""

# Test 5: Get Contacts
echo "Test 5: Get Contacts"
echo "-----------------------------------"
curl -s -X GET "$BASE_URL/contacts" \
  -H "Authorization: Bearer $SESSION_TOKEN"
echo ""
echo ""

# Test 6: Add Second Email (Should trigger notification)
echo "Test 6: Add Second Email (Check server console for notification)"
echo "-----------------------------------"
curl -s -X POST "$BASE_URL/contacts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SESSION_TOKEN" \
  -d "{\"contact_type\":\"email\",\"contact_value\":\"test2@example.com\"}"
echo ""
echo ""

# Test 7: Request OTP
echo "Test 7: Request OTP for email"
echo "-----------------------------------"
OTP_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/request-otp" \
  -H "Content-Type: application/json" \
  -d "{\"contact_type\":\"email\",\"contact_value\":\"test@example.com\"}")
echo "Response: $OTP_RESPONSE"
OTP_CODE=$(echo $OTP_RESPONSE | grep -o '"otp_code":"[^"]*"' | cut -d'"' -f4)
echo "OTP Code: $OTP_CODE"
echo ""

# Test 8: Verify OTP with new device
echo "Test 8: Verify OTP with new device"
echo "-----------------------------------"
NEW_DEVICE_ID="test-device-otp-$(date +%s)"
curl -s -X POST "$BASE_URL/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d "{\"contact_value\":\"test@example.com\",\"otp_code\":\"$OTP_CODE\",\"device_id\":\"$NEW_DEVICE_ID\"}"
echo ""
echo ""

# Test 9: Register with Token
echo "Test 9: Register with Token"
echo "-----------------------------------"
TOKEN_DEVICE_ID="test-device-token-$(date +%s)"
curl -s -X POST "$BASE_URL/auth/token" \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"1111-2222-3333-4444\",\"device_id\":\"$TOKEN_DEVICE_ID\"}"
echo ""
echo ""

# Test 10: Admin View
echo "Test 10: Admin View (All Registrations)"
echo "-----------------------------------"
curl -s -X GET "$BASE_URL/admin/registrations" | python3 -m json.tool 2>/dev/null || echo "JSON parsing failed"
echo ""
echo ""

echo "================================"
echo "Testing Complete!"
echo "================================"
echo ""
echo "Visit these URLs in your browser:"
echo "- Main Login: http://localhost:5000/"
echo "- MediaZone: http://localhost:5000/mediazone/index.html"
echo "- Admin View: http://localhost:5000/frontend/admin.html"
echo "- Account Management: http://localhost:5000/frontend/account.html"
