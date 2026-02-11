from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import database as db
import auth
import os

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, static_folder=project_root)
CORS(app)

# Initialize database on startup
db.init_db()

@app.route('/api/auth/accreditation', methods=['POST'])
def auth_accreditation():
    """Authenticate with accreditation number and CVV."""
    data = request.json
    accreditation_number = data.get('accreditation_number')
    accreditation_cvv = data.get('accreditation_cvv')
    device_id = data.get('device_id')

    if not device_id:
        return jsonify({'success': False, 'error': 'Device ID is required'}), 400

    # Validate format
    valid, error = auth.validate_accreditation_format(accreditation_number, accreditation_cvv)
    if not valid:
        return jsonify({'success': False, 'error': error}), 400

    # Find or create user
    user = db.get_user_by_accreditation(accreditation_number)
    if not user:
        user_id = db.create_user(
            accreditation_number=accreditation_number,
            accreditation_cvv=accreditation_cvv
        )
    else:
        user_id = user['id']
        # Verify CVV matches
        if user['accreditation_cvv'] != accreditation_cvv:
            return jsonify({'success': False, 'error': 'Invalid CVV'}), 401

    # Create device session
    session_token, error = db.create_device(device_id, user_id)

    if error:
        return jsonify({'success': False, 'error': error}), 403

    return jsonify({
        'success': True,
        'user_id': user_id,
        'session_token': session_token
    })

@app.route('/api/auth/token', methods=['POST'])
def auth_token():
    """Authenticate with third-party token."""
    data = request.json
    token = data.get('token')
    device_id = data.get('device_id')

    if not device_id:
        return jsonify({'success': False, 'error': 'Device ID is required'}), 400

    # Validate format
    valid, error = auth.validate_token_format(token)
    if not valid:
        return jsonify({'success': False, 'error': error}), 400

    # Find or create user
    user = db.get_user_by_token(token)
    if not user:
        user_id = db.create_user(token=token)
    else:
        user_id = user['id']

    # Create device session
    session_token, error = db.create_device(device_id, user_id)

    if error:
        return jsonify({'success': False, 'error': error}), 403

    return jsonify({
        'success': True,
        'user_id': user_id,
        'session_token': session_token
    })

@app.route('/api/auth/request-otp', methods=['POST'])
def request_otp():
    """Request OTP for email or phone."""
    data = request.json
    contact_type = data.get('contact_type')
    contact_value = data.get('contact_value')

    if contact_type not in ['email', 'phone']:
        return jsonify({'success': False, 'error': 'Invalid contact type'}), 400

    # Validate format
    if contact_type == 'email':
        valid, error = auth.validate_email(contact_value)
    else:
        valid, error = auth.validate_phone(contact_value)

    if not valid:
        return jsonify({'success': False, 'error': error}), 400

    # Check if contact is registered
    user = db.get_user_by_contact(contact_value)
    if not user:
        return jsonify({'success': False, 'error': 'Contact not registered'}), 404

    # Generate OTP
    otp_code = auth.generate_otp()
    db.create_otp_session(contact_value, otp_code)

    # For demo: return OTP in response
    print(f"OTP for {contact_value}: {otp_code}")

    return jsonify({
        'success': True,
        'otp_code': otp_code,  # Demo only - would not return in production
        'message': f'OTP sent to {contact_value}'
    })

@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and create device session."""
    data = request.json
    contact_value = data.get('contact_value')
    otp_code = data.get('otp_code')
    device_id = data.get('device_id')

    if not all([contact_value, otp_code, device_id]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    # Verify OTP
    if not db.verify_otp(contact_value, otp_code):
        return jsonify({'success': False, 'error': 'Invalid or expired OTP'}), 401

    # Get user by contact
    user = db.get_user_by_contact(contact_value)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    # Create device session
    session_token, error = db.create_device(device_id, user['id'])

    if error:
        return jsonify({'success': False, 'error': error}), 403

    return jsonify({
        'success': True,
        'user_id': user['id'],
        'session_token': session_token
    })

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Check if device is authenticated."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'authenticated': False}), 401

    device_id = auth_header.replace('Bearer ', '')
    device = db.verify_device(device_id)

    if device:
        return jsonify({
            'authenticated': True,
            'user_id': device['user_id']
        })
    else:
        return jsonify({'authenticated': False}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout and remove device session."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401

    device_id = auth_header.replace('Bearer ', '')
    db.delete_device(device_id)

    return jsonify({'success': True})

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Get user's contacts."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Not authenticated'}), 401

    device_id = auth_header.replace('Bearer ', '')
    device = db.verify_device(device_id)

    if not device:
        return jsonify({'error': 'Invalid session'}), 401

    contacts = db.get_user_contacts(device['user_id'])

    return jsonify({'contacts': contacts})

@app.route('/api/contacts', methods=['POST'])
def add_contact():
    """Add a contact for the user."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Not authenticated'}), 401

    device_id = auth_header.replace('Bearer ', '')
    device = db.verify_device(device_id)

    if not device:
        return jsonify({'error': 'Invalid session'}), 401

    data = request.json
    contact_type = data.get('contact_type')
    contact_value = data.get('contact_value')

    if contact_type not in ['email', 'phone']:
        return jsonify({'success': False, 'error': 'Invalid contact type'}), 400

    # Validate format
    if contact_type == 'email':
        valid, error = auth.validate_email(contact_value)
    else:
        valid, error = auth.validate_phone(contact_value)

    if not valid:
        return jsonify({'success': False, 'error': error}), 400

    # Check limit
    count = db.count_user_contacts_by_type(device['user_id'], contact_type)
    if count >= 2:
        return jsonify({'success': False, 'error': f'Maximum 2 {contact_type}s allowed'}), 400

    # Add contact
    try:
        contact_id = db.add_contact(device['user_id'], contact_type, contact_value)

        # If this is the second contact, notify the primary
        if count == 1:
            primary = db.get_primary_contact(device['user_id'], contact_type)
            if primary:
                print(f"NOTIFICATION to {primary['contact_value']}: A second {contact_type} has been added to your account")

        return jsonify({'success': True, 'contact_id': contact_id})
    except Exception as e:
        return jsonify({'success': False, 'error': 'Contact already exists or database error'}), 400

@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
def remove_contact(contact_id):
    """Remove a contact."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Not authenticated'}), 401

    device_id = auth_header.replace('Bearer ', '')
    device = db.verify_device(device_id)

    if not device:
        return jsonify({'error': 'Invalid session'}), 401

    db.delete_contact(contact_id, device['user_id'])

    return jsonify({'success': True})

@app.route('/api/admin/registrations', methods=['GET'])
def admin_registrations():
    """Get all registrations for admin view."""
    users = db.get_all_users_with_details()
    return jsonify({'users': users})

# Serve static files for frontend
@app.route('/')
def index():
    return send_from_directory(os.path.join(project_root, 'frontend'), 'index.html')

# Serve CSS, JS and other static files from root path
@app.route('/styles.css')
def serve_styles():
    return send_from_directory(os.path.join(project_root, 'frontend'), 'styles.css')

@app.route('/auth.js')
def serve_auth_js():
    return send_from_directory(os.path.join(project_root, 'frontend'), 'auth.js')

@app.route('/account.js')
def serve_account_js():
    return send_from_directory(os.path.join(project_root, 'frontend'), 'account.js')

@app.route('/registration-help.png')
def serve_help_image():
    return send_from_directory(os.path.join(project_root, 'frontend'), 'registration-help.png')

@app.route('/frontend/<path:path>')
def serve_frontend(path):
    return send_from_directory(os.path.join(project_root, 'frontend'), path)

@app.route('/mediazone/<path:path>')
def serve_mediazone(path):
    return send_from_directory(os.path.join(project_root, 'mediazone'), path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
