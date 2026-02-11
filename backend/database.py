import sqlite3
from datetime import datetime, timedelta
import os

# Use /data/sarp.db on Railway (persistent volume), fall back to local path for development
DB_PATH = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sarp.db'))

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            accreditation_number TEXT UNIQUE,
            accreditation_cvv TEXT,
            token TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Contacts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            contact_type TEXT NOT NULL,
            contact_value TEXT NOT NULL,
            is_primary BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, contact_type, contact_value)
        )
    ''')

    # Apps table - defines all available apps
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_code TEXT UNIQUE NOT NULL,
            app_name TEXT NOT NULL,
            max_sessions INTEGER DEFAULT 3,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert default apps if not exists
    cursor.execute('''
        INSERT OR IGNORE INTO apps (id, app_code, app_name, max_sessions) VALUES
        (1, 'mediazone', 'MediaZone', 3),
        (2, 'transport', 'Transportation', 3),
        (3, 'wifi', 'Wifi', 3),
        (4, 'remote-cis', 'Remote CIS', 3),
        (5, 'weather', 'Weather', 3),
        (6, 'seat', 'SEAT', 3)
    ''')

    # Accreditation apps - defines which apps each accreditation has access to
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accreditation_apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            accreditation_number TEXT NOT NULL,
            app_id INTEGER NOT NULL,
            authorized BOOLEAN DEFAULT 1,
            FOREIGN KEY (app_id) REFERENCES apps(id),
            UNIQUE(accreditation_number, app_id)
        )
    ''')

    # App sessions table - tracks device access per app (replaces old devices table concept)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            app_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (app_id) REFERENCES apps(id),
            UNIQUE(device_id, app_id)
        )
    ''')

    # Keep old devices table for backward compatibility (will be migrated to app_sessions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            app_id INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (app_id) REFERENCES apps(id)
        )
    ''')

    # OTP sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otp_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_value TEXT NOT NULL,
            otp_code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            verified BOOLEAN DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_user(accreditation_number=None, accreditation_cvv=None, token=None):
    """Create a new user."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        'INSERT INTO users (accreditation_number, accreditation_cvv, token) VALUES (?, ?, ?)',
        (accreditation_number, accreditation_cvv, token)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_user_by_accreditation(accreditation_number):
    """Get user by accreditation number."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE accreditation_number = ?', (accreditation_number,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_token(token):
    """Get user by token."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE token = ?', (token,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_contact(contact_value):
    """Get user by contact (email or phone)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.* FROM users u
        JOIN contacts c ON u.id = c.user_id
        WHERE c.contact_value = ?
    ''', (contact_value,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def create_device(device_id, user_id):
    """
    Create or update device session (90-day expiry).
    Returns (device_id, None) on success or (None, error_message) on failure.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Check if device exists
    cursor.execute('SELECT id FROM devices WHERE device_id = ?', (device_id,))
    existing = cursor.fetchone()

    # If this is a new device, check device limits
    if not existing:
        # Check if user has email - if not, enforce 3-device limit
        if not user_has_email(user_id):
            active_count = count_active_devices(user_id)
            if active_count >= 3:
                conn.close()
                return None, "Device limit reached (3 devices max). Add an email address to your account for multiple devices."

    expires_at = datetime.now() + timedelta(days=90)

    if existing:
        cursor.execute(
            'UPDATE devices SET user_id = ?, expires_at = ? WHERE device_id = ?',
            (user_id, expires_at, device_id)
        )
    else:
        cursor.execute(
            'INSERT INTO devices (device_id, user_id, expires_at) VALUES (?, ?, ?)',
            (device_id, user_id, expires_at)
        )

    conn.commit()
    conn.close()
    return device_id, None

def verify_device(device_id):
    """Check if device is valid and not expired."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM devices WHERE device_id = ? AND expires_at > ?',
        (device_id, datetime.now())
    )
    device = cursor.fetchone()
    conn.close()
    return dict(device) if device else None

def delete_device(device_id):
    """Remove device session."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM devices WHERE device_id = ?', (device_id,))
    conn.commit()
    conn.close()

def count_active_devices(user_id):
    """Count active (non-expired) devices for a user."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT COUNT(*) as count FROM devices WHERE user_id = ? AND expires_at > ?',
        (user_id, datetime.now())
    )
    result = cursor.fetchone()
    conn.close()
    return result['count']

def user_has_email(user_id):
    """Check if user has any email contacts."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT COUNT(*) as count FROM contacts WHERE user_id = ? AND contact_type = ?',
        (user_id, 'email')
    )
    result = cursor.fetchone()
    conn.close()
    return result['count'] > 0

def get_user_contacts(user_id):
    """Get all contacts for a user."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM contacts WHERE user_id = ? ORDER BY contact_type, created_at',
        (user_id,)
    )
    contacts = cursor.fetchall()
    conn.close()
    return [dict(c) for c in contacts]

def count_user_contacts_by_type(user_id, contact_type):
    """Count contacts of a specific type for a user."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT COUNT(*) as count FROM contacts WHERE user_id = ? AND contact_type = ?',
        (user_id, contact_type)
    )
    result = cursor.fetchone()
    conn.close()
    return result['count']

def add_contact(user_id, contact_type, contact_value):
    """Add a contact for a user."""
    conn = get_db()
    cursor = conn.cursor()

    # Set is_primary to 1 if this is the first contact of this type
    count = count_user_contacts_by_type(user_id, contact_type)
    is_primary = 1 if count == 0 else 0

    cursor.execute(
        'INSERT INTO contacts (user_id, contact_type, contact_value, is_primary) VALUES (?, ?, ?, ?)',
        (user_id, contact_type, contact_value, is_primary)
    )
    contact_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return contact_id

def get_primary_contact(user_id, contact_type):
    """Get primary contact of a specific type for notification."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM contacts WHERE user_id = ? AND contact_type = ? AND is_primary = 1',
        (user_id, contact_type)
    )
    contact = cursor.fetchone()
    conn.close()
    return dict(contact) if contact else None

def delete_contact(contact_id, user_id):
    """Delete a contact."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contacts WHERE id = ? AND user_id = ?', (contact_id, user_id))
    conn.commit()
    conn.close()

def create_otp_session(contact_value, otp_code):
    """Create OTP session (5 minute expiry)."""
    conn = get_db()
    cursor = conn.cursor()

    expires_at = datetime.now() + timedelta(minutes=5)
    cursor.execute(
        'INSERT INTO otp_sessions (contact_value, otp_code, expires_at) VALUES (?, ?, ?)',
        (contact_value, otp_code, expires_at)
    )

    conn.commit()
    conn.close()

def verify_otp(contact_value, otp_code):
    """Verify OTP is valid and not expired."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM otp_sessions WHERE contact_value = ? AND otp_code = ? AND expires_at > ? AND verified = 0',
        (contact_value, otp_code, datetime.now())
    )
    session = cursor.fetchone()

    if session:
        # Mark as verified
        cursor.execute('UPDATE otp_sessions SET verified = 1 WHERE id = ?', (session['id'],))
        conn.commit()

    conn.close()
    return session is not None

def get_all_users_with_details():
    """Get all users with their contacts and device count for admin view."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            u.id,
            u.accreditation_number,
            u.token,
            u.created_at,
            COUNT(DISTINCT d.id) as device_count
        FROM users u
        LEFT JOIN devices d ON u.id = d.user_id AND d.expires_at > ?
        GROUP BY u.id
        ORDER BY u.created_at DESC
    ''', (datetime.now(),))

    users = [dict(u) for u in cursor.fetchall()]

    # Get contacts and devices for each user
    for user in users:
        user['contacts'] = get_user_contacts(user['id'])

        # Get active devices
        cursor.execute('''
            SELECT device_id, created_at, expires_at
            FROM devices
            WHERE user_id = ? AND expires_at > ?
            ORDER BY created_at DESC
        ''', (user['id'], datetime.now()))
        user['devices'] = [dict(d) for d in cursor.fetchall()]

    conn.close()
    return users

# ============================================================================
# Multi-App Functions (future expansion)
# ============================================================================

def get_app_by_code(app_code):
    """Get app by code (e.g., 'mediazone')."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM apps WHERE app_code = ? AND active = 1', (app_code,))
    app = cursor.fetchone()
    conn.close()
    return dict(app) if app else None

def get_all_apps():
    """Get all active apps."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM apps WHERE active = 1 ORDER BY id')
    apps = cursor.fetchall()
    conn.close()
    return [dict(a) for a in apps]

def get_authorized_apps_for_accreditation(accreditation_number):
    """Get list of apps this accreditation has access to."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*
        FROM apps a
        JOIN accreditation_apps aa ON a.id = aa.app_id
        WHERE aa.accreditation_number = ? AND aa.authorized = 1 AND a.active = 1
    ''', (accreditation_number,))
    apps = cursor.fetchall()
    conn.close()
    return [dict(a) for a in apps]

def set_accreditation_app_access(accreditation_number, app_id, authorized=True):
    """Set whether an accreditation has access to an app."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO accreditation_apps (accreditation_number, app_id, authorized)
        VALUES (?, ?, ?)
    ''', (accreditation_number, app_id, authorized))
    conn.commit()
    conn.close()

def create_app_session(device_id, user_id, app_id):
    """
    Create or update app session for a specific app (90-day expiry).
    Returns (device_id, None) on success or (None, error_message) on failure.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Check if session exists for this device+app combination
    cursor.execute('''
        SELECT id FROM app_sessions
        WHERE device_id = ? AND app_id = ?
    ''', (device_id, app_id))
    existing = cursor.fetchone()

    # If this is a new session, check session limits for this app
    if not existing:
        # Get app max_sessions (or check if user has email for unlimited)
        if not user_has_email(user_id):
            cursor.execute('SELECT max_sessions FROM apps WHERE id = ?', (app_id,))
            app = cursor.fetchone()
            max_sessions = app['max_sessions'] if app else 3

            # Count active sessions for this user+app
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM app_sessions
                WHERE user_id = ? AND app_id = ? AND expires_at > ?
            ''', (user_id, app_id, datetime.now()))
            active_count = cursor.fetchone()['count']

            if active_count >= max_sessions:
                conn.close()
                return None, f"Device limit reached ({max_sessions} devices max). Add an email address to your account for multiple devices."

    expires_at = datetime.now() + timedelta(days=90)

    if existing:
        cursor.execute('''
            UPDATE app_sessions
            SET user_id = ?, expires_at = ?
            WHERE device_id = ? AND app_id = ?
        ''', (user_id, expires_at, device_id, app_id))
    else:
        cursor.execute('''
            INSERT INTO app_sessions (device_id, user_id, app_id, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (device_id, user_id, app_id, expires_at))

    conn.commit()
    conn.close()
    return device_id, None

def get_user_app_sessions(user_id):
    """Get all active app sessions for a user."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT aps.*, a.app_name, a.app_code
        FROM app_sessions aps
        JOIN apps a ON aps.app_id = a.id
        WHERE aps.user_id = ? AND aps.expires_at > ?
        ORDER BY a.app_name
    ''', (user_id, datetime.now()))
    sessions = cursor.fetchall()
    conn.close()
    return [dict(s) for s in sessions]
