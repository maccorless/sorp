const API_BASE = window.location.origin + '/api';

function getSessionToken() {
    return localStorage.getItem('session_token');
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

async function checkAuth() {
    const sessionToken = getSessionToken();
    if (!sessionToken) {
        window.location.href = '/';
        return false;
    }

    try {
        const response = await fetch(`${API_BASE}/auth/check`, {
            headers: { 'Authorization': `Bearer ${sessionToken}` }
        });

        if (!response.ok) {
            window.location.href = '/';
            return false;
        }

        return true;
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.href = '/';
        return false;
    }
}

async function loadContacts() {
    const sessionToken = getSessionToken();

    try {
        const response = await fetch(`${API_BASE}/contacts`, {
            headers: { 'Authorization': `Bearer ${sessionToken}` }
        });

        const data = await response.json();

        if (data.contacts) {
            displayContacts(data.contacts);
        }
    } catch (error) {
        showError('Failed to load contacts');
        console.error(error);
    }
}

function displayContacts(contacts) {
    const emails = contacts.filter(c => c.contact_type === 'email');
    const phones = contacts.filter(c => c.contact_type === 'phone');

    // Display emails
    const emailList = document.getElementById('email-list');
    emailList.innerHTML = '';
    if (emails.length === 0) {
        emailList.innerHTML = '<li class="contact-item">No email addresses added</li>';
    } else {
        emails.forEach(email => {
            const li = document.createElement('li');
            li.className = 'contact-item';
            li.innerHTML = `
                <div>
                    <span class="contact-value">${email.contact_value}</span>
                    ${email.is_primary ? '<span class="contact-badge">Primary</span>' : ''}
                </div>
                <button class="btn btn-small btn-danger" onclick="removeContact(${email.id})">Remove</button>
            `;
            emailList.appendChild(li);
        });
    }

    // Display phones
    const phoneList = document.getElementById('phone-list');
    phoneList.innerHTML = '';
    if (phones.length === 0) {
        phoneList.innerHTML = '<li class="contact-item">No phone numbers added</li>';
    } else {
        phones.forEach(phone => {
            const li = document.createElement('li');
            li.className = 'contact-item';
            li.innerHTML = `
                <div>
                    <span class="contact-value">${phone.contact_value}</span>
                    ${phone.is_primary ? '<span class="contact-badge">Primary</span>' : ''}
                </div>
                <button class="btn btn-small btn-danger" onclick="removeContact(${phone.id})">Remove</button>
            `;
            phoneList.appendChild(li);
        });
    }

    // Show/hide add buttons based on limits
    document.getElementById('add-email-btn').style.display = emails.length >= 2 ? 'none' : 'inline-block';
    document.getElementById('add-phone-btn').style.display = phones.length >= 2 ? 'none' : 'inline-block';
}

async function addContact(contactType, contactValue) {
    const sessionToken = getSessionToken();

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
            showSuccess(`${contactType === 'email' ? 'Email' : 'Phone'} added successfully!`);
            loadContacts();
            return true;
        } else {
            showError(data.error || 'Failed to add contact');
            return false;
        }
    } catch (error) {
        showError('Network error. Please try again.');
        console.error(error);
        return false;
    }
}

async function removeContact(contactId) {
    if (!confirm('Are you sure you want to remove this contact?')) {
        return;
    }

    const sessionToken = getSessionToken();

    try {
        const response = await fetch(`${API_BASE}/contacts/${contactId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${sessionToken}` }
        });

        const data = await response.json();

        if (data.success) {
            showSuccess('Contact removed successfully!');
            loadContacts();
        } else {
            showError('Failed to remove contact');
        }
    } catch (error) {
        showError('Network error. Please try again.');
        console.error(error);
    }
}

async function logout() {
    const sessionToken = getSessionToken();

    try {
        await fetch(`${API_BASE}/auth/logout`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${sessionToken}` }
        });

        localStorage.removeItem('session_token');
        localStorage.removeItem('user_id');
        window.location.href = '/';
    } catch (error) {
        console.error('Logout error:', error);
        // Still clear local data and redirect
        localStorage.removeItem('session_token');
        localStorage.removeItem('user_id');
        window.location.href = '/';
    }
}

// Email form handlers
document.getElementById('add-email-btn').addEventListener('click', () => {
    document.getElementById('add-email-form').style.display = 'block';
    document.getElementById('add-email-btn').style.display = 'none';
});

document.getElementById('cancel-email-btn').addEventListener('click', () => {
    document.getElementById('add-email-form').style.display = 'none';
    document.getElementById('add-email-btn').style.display = 'inline-block';
    document.getElementById('new-email').value = '';
});

document.getElementById('save-email-btn').addEventListener('click', async () => {
    const email = document.getElementById('new-email').value;
    if (!email) {
        showError('Please enter an email address');
        return;
    }

    const success = await addContact('email', email);
    if (success) {
        document.getElementById('add-email-form').style.display = 'none';
        document.getElementById('new-email').value = '';
    }
});

// Phone form handlers
document.getElementById('add-phone-btn').addEventListener('click', () => {
    document.getElementById('add-phone-form').style.display = 'block';
    document.getElementById('add-phone-btn').style.display = 'none';
});

document.getElementById('cancel-phone-btn').addEventListener('click', () => {
    document.getElementById('add-phone-form').style.display = 'none';
    document.getElementById('add-phone-btn').style.display = 'inline-block';
    document.getElementById('new-phone').value = '';
});

document.getElementById('save-phone-btn').addEventListener('click', async () => {
    const phone = document.getElementById('new-phone').value;
    if (!phone) {
        showError('Please enter a phone number');
        return;
    }

    const success = await addContact('phone', phone);
    if (success) {
        document.getElementById('add-phone-form').style.display = 'none';
        document.getElementById('new-phone').value = '';
    }
});

// Logout handler
document.getElementById('logout-btn').addEventListener('click', logout);

// Initialize page
checkAuth().then(authenticated => {
    if (authenticated) {
        loadContacts();
    }
});
