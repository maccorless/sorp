const API_BASE = 'http://localhost:5000/api';

function getSessionToken() {
    return localStorage.getItem('session_token');
}

async function checkAuth() {
    const sessionToken = getSessionToken();

    // If no session token, redirect to login immediately
    if (!sessionToken) {
        console.log('No session token found, redirecting to login');
        window.location.href = '/';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/auth/check`, {
            headers: { 'Authorization': `Bearer ${sessionToken}` }
        });

        if (!response.ok) {
            console.log('Session invalid or expired, redirecting to login');
            localStorage.removeItem('session_token');
            localStorage.removeItem('user_id');
            window.location.href = '/';
            return;
        }

        const data = await response.json();
        console.log('Authenticated as user:', data.user_id);
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.href = '/';
    }
}

async function logout() {
    const sessionToken = getSessionToken();

    try {
        await fetch(`${API_BASE}/auth/logout`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${sessionToken}` }
        });
    } catch (error) {
        console.error('Logout error:', error);
    }

    // Clear local storage and redirect to login
    localStorage.removeItem('session_token');
    localStorage.removeItem('user_id');
    window.location.href = '/';
}

// Attach logout handler to button
const logoutBtn = document.getElementById('logout-btn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
}

// Check auth on page load
checkAuth();
