const API_BASE = window.location.origin + '/api';

// Initialize device ID
function getOrCreateDeviceId() {
    let deviceId = localStorage.getItem('device_id');
    if (!deviceId) {
        deviceId = generateUUID();
        localStorage.setItem('device_id', deviceId);
    }
    return deviceId;
}

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function showError(message) {
    const container = document.getElementById('error-container');
    container.innerHTML = `<div class="error-message">${message}</div>`;
    setTimeout(() => container.innerHTML = '', 5000);
}

function showSuccess(message) {
    const container = document.getElementById('success-container');
    container.innerHTML = `<div class="success-message">${message}</div>`;
    setTimeout(() => container.innerHTML = '', 5000);
}

function storeSession(sessionToken, userId) {
    localStorage.setItem('session_token', sessionToken);
    localStorage.setItem('user_id', userId);
}

function redirectToMediaZone() {
    window.location.href = '/mediazone/index.html';
}

// Show kiosk mode modal
function showKioskModal() {
    const modal = document.getElementById('kiosk-modal');
    modal.style.display = 'flex';
}

function hideKioskModal() {
    const modal = document.getElementById('kiosk-modal');
    modal.style.display = 'none';
}

// Tab switching
document.querySelectorAll('.auth-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));

        tab.classList.add('active');
        const method = tab.dataset.method;
        document.getElementById(`${method}-form`).classList.add('active');
    });
});

// Accreditation form
document.getElementById('accreditation-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const accreditationNumber = document.getElementById('accreditation-number').value;
    const accreditationCvv = document.getElementById('accreditation-cvv').value;
    const deviceId = getOrCreateDeviceId();
    const kioskMode = document.getElementById('accred-kiosk-mode').checked;

    try {
        const response = await fetch(`${API_BASE}/auth/accreditation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                accreditation_number: accreditationNumber,
                accreditation_cvv: accreditationCvv,
                device_id: deviceId
            })
        });

        const data = await response.json();

        if (data.success) {
            storeSession(data.session_token, data.user_id);
            showSuccess('Authentication successful!');

            // If kiosk mode is enabled, show modal to add contact
            if (kioskMode) {
                setTimeout(showKioskModal, 500);
            } else {
                setTimeout(redirectToMediaZone, 1000);
            }
        } else {
            showError(data.error || 'Authentication failed');
        }
    } catch (error) {
        showError('Network error. Please try again.');
        console.error(error);
    }
});

// Token form
document.getElementById('token-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const token = document.getElementById('token').value;
    const deviceId = getOrCreateDeviceId();
    const kioskMode = document.getElementById('token-kiosk-mode').checked;

    try {
        const response = await fetch(`${API_BASE}/auth/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token: token,
                device_id: deviceId
            })
        });

        const data = await response.json();

        if (data.success) {
            storeSession(data.session_token, data.user_id);
            showSuccess('Authentication successful!');

            // If kiosk mode is enabled, show modal to add contact
            if (kioskMode) {
                setTimeout(showKioskModal, 500);
            } else {
                setTimeout(redirectToMediaZone, 1000);
            }
        } else {
            showError(data.error || 'Authentication failed');
        }
    } catch (error) {
        showError('Network error. Please try again.');
        console.error(error);
    }
});

// Get selected contact type from OTP form
function getOTPContactType() {
    const radios = document.getElementsByName('contact-type');
    for (const radio of radios) {
        if (radio.checked) {
            return radio.value;
        }
    }
    return 'email';
}

// OTP form - Request OTP
document.getElementById('request-otp-btn').addEventListener('click', async () => {
    const contactType = getOTPContactType();
    const contactValue = document.getElementById('contact-value').value;

    if (!contactValue) {
        showError('Please enter your email or phone number');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/auth/request-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contact_type: contactType,
                contact_value: contactValue
            })
        });

        const data = await response.json();

        if (data.success) {
            // Show OTP (demo only)
            document.getElementById('otp-code-display').textContent = data.otp_code;
            document.getElementById('otp-request-step').style.display = 'none';
            document.getElementById('otp-verify-step').style.display = 'block';
            showSuccess('OTP sent! (Displayed above for demo)');
        } else {
            showError(data.error || 'Failed to send OTP. Make sure this contact is registered.');
        }
    } catch (error) {
        showError('Network error. Please try again.');
        console.error(error);
    }
});

// OTP form - Verify OTP
document.getElementById('otp-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const contactValue = document.getElementById('contact-value').value;
    const otpCode = document.getElementById('otp-code').value;
    const deviceId = getOrCreateDeviceId();

    try {
        const response = await fetch(`${API_BASE}/auth/verify-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contact_value: contactValue,
                otp_code: otpCode,
                device_id: deviceId
            })
        });

        const data = await response.json();

        if (data.success) {
            storeSession(data.session_token, data.user_id);
            showSuccess('Authentication successful! Redirecting...');
            setTimeout(redirectToMediaZone, 1000);
        } else {
            showError(data.error || 'Invalid OTP');
        }
    } catch (error) {
        showError('Network error. Please try again.');
        console.error(error);
    }
});

// Back button in OTP form
document.getElementById('back-to-request').addEventListener('click', () => {
    document.getElementById('otp-request-step').style.display = 'block';
    document.getElementById('otp-verify-step').style.display = 'none';
    document.getElementById('otp-code').value = '';
});

// Auto-format token input
document.getElementById('token').addEventListener('input', (e) => {
    let value = e.target.value.replace(/[^0-9]/g, '');
    if (value.length > 16) value = value.slice(0, 16);

    const formatted = value.match(/.{1,4}/g)?.join('-') || value;
    e.target.value = formatted;
});

// Kiosk Modal - Get selected contact type
function getKioskContactType() {
    const radios = document.getElementsByName('kiosk-contact-type');
    for (const radio of radios) {
        if (radio.checked) {
            return radio.value;
        }
    }
    return 'email';
}

// Kiosk Modal - Add contact
document.getElementById('kiosk-add-btn').addEventListener('click', async () => {
    const contactType = getKioskContactType();
    const contactValue = document.getElementById('kiosk-contact-value').value;
    const sessionToken = localStorage.getItem('session_token');
    const errorDiv = document.getElementById('kiosk-error');

    if (!contactValue) {
        errorDiv.textContent = 'Please enter a contact';
        errorDiv.style.display = 'block';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/contacts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${sessionToken}`
            },
            body: JSON.stringify({
                contact_type: contactType,
                contact_value: contactValue
            })
        });

        const data = await response.json();

        if (data.success) {
            hideKioskModal();
            showSuccess(`${contactType === 'email' ? 'Email' : 'Phone'} added! You now have multiple device access. Redirecting...`);
            setTimeout(redirectToMediaZone, 2000);
        } else {
            errorDiv.textContent = data.error || 'Failed to add contact';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.textContent = 'Network error. Please try again.';
        errorDiv.style.display = 'block';
        console.error(error);
    }
});

// Kiosk Modal - Skip
document.getElementById('kiosk-skip-btn').addEventListener('click', () => {
    hideKioskModal();
    showSuccess('You can add a contact later in Account Management. Redirecting...');
    setTimeout(redirectToMediaZone, 1500);
});

// Check if user is already logged in and show logout button
async function checkExistingSession() {
    const sessionToken = localStorage.getItem('session_token');
    const logoutBtn = document.getElementById('main-logout-btn');

    if (!sessionToken || !logoutBtn) return;

    try {
        const response = await fetch(`${API_BASE}/auth/check`, {
            headers: { 'Authorization': `Bearer ${sessionToken}` }
        });

        if (response.ok) {
            logoutBtn.style.display = 'inline-block';
        }
    } catch (error) {
        console.log('Not authenticated');
    }
}

// Logout from main page
async function logoutFromMainPage() {
    const sessionToken = localStorage.getItem('session_token');

    try {
        await fetch(`${API_BASE}/auth/logout`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${sessionToken}` }
        });
    } catch (error) {
        console.error('Logout error:', error);
    }

    localStorage.removeItem('session_token');
    localStorage.removeItem('user_id');

    showSuccess('Logged out successfully');

    const logoutBtn = document.getElementById('main-logout-btn');
    if (logoutBtn) {
        logoutBtn.style.display = 'none';
    }
}

// Attach logout handler
const mainLogoutBtn = document.getElementById('main-logout-btn');
if (mainLogoutBtn) {
    mainLogoutBtn.addEventListener('click', logoutFromMainPage);
}

// Check for existing session on page load
checkExistingSession();
