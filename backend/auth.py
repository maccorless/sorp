import re
import random
import string

def validate_accreditation_format(accreditation_number, accreditation_cvv):
    """Validate accreditation number (8 digits) and CVV (4 digits)."""
    if not accreditation_number or not accreditation_cvv:
        return False, "Accreditation number and CVV are required"

    if not re.match(r'^\d{8}$', accreditation_number):
        return False, "Accreditation number must be exactly 8 digits"

    if not re.match(r'^\d{4}$', accreditation_cvv):
        return False, "CVV must be exactly 4 digits"

    return True, None

def validate_token_format(token):
    """Validate token format (####-####-####-####)."""
    if not token:
        return False, "Token is required"

    if not re.match(r'^\d{4}-\d{4}-\d{4}-\d{4}$', token):
        return False, "Token must be in format ####-####-####-####"

    return True, None

def validate_email(email):
    """Basic email validation."""
    if not email:
        return False, "Email is required"

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return False, "Invalid email format"

    return True, None

def validate_phone(phone):
    """Basic phone validation (flexible format)."""
    if not phone:
        return False, "Phone number is required"

    # Remove common formatting characters
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)

    if not re.match(r'^\+?\d{10,15}$', clean_phone):
        return False, "Invalid phone number format"

    return True, None

def generate_otp():
    """Generate a 6-digit OTP code."""
    return ''.join(random.choices(string.digits, k=6))

def generate_device_id():
    """Generate a UUID-like device ID."""
    import uuid
    return str(uuid.uuid4())
