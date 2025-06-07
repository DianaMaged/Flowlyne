// Global config - FIXED: Use correct Django port
const API_BASE_URL = 'http://localhost:8000/api';

// Token helpers
function setAuthToken(token) {
    localStorage.setItem('flowlyne_token', token);  // Use consistent token key
}

function getAuthToken() {
    return localStorage.getItem('flowlyne_token');
}

function clearAuthToken() {
    localStorage.removeItem('flowlyne_token');
    localStorage.removeItem('flowlyne_current_company');
}

// CSRF Token helper
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
        document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

// Generic API call - FIXED: Use Token authentication format
async function apiRequest(endpoint, options = {}) {
    const token = getAuthToken();
    const headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
        ...options.headers
    };
    
    // FIXED: Use Django Token format instead of Bearer
    if (token) {
        headers['Authorization'] = `Token ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
}

// Login - FIXED: Use correct endpoint and data format
async function handleLogin(event) {
    event.preventDefault();

    const loginData = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };

    try {
        const response = await apiRequest('/login/', {  // FIXED: Remove extra slash
            method: 'POST',
            body: JSON.stringify(loginData)
        });

        // Store token and company data
        localStorage.setItem('flowlyne_token', response.token);
        localStorage.setItem('flowlyne_current_company', JSON.stringify(response.company));
        
        // Redirect to dashboard
        window.location.href = '/dashboard/';
    } catch (error) {
        console.error('Login error:', error);
        alert('Login failed: ' + error.message);
    }
}

// Register - FIXED: Use correct field names
async function handleRegister(event) {
    event.preventDefault();

    const registerData = {
        company_name: document.getElementById('company_name').value,  // FIXED: Use correct field name
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        description: document.getElementById('description').value
    };

    try {
        const response = await apiRequest('/register/', {
            method: 'POST',
            body: JSON.stringify(registerData)
        });

        // Store token and company data
        setAuthToken(response.token);
        localStorage.setItem('flowlyne_current_company', JSON.stringify(response.company));
        
        window.location.href = '/services/';
    } catch (error) {
        console.error('Registration error:', error);
        alert('Registration failed: ' + error.message);
    }
}

// Check authentication status
function checkAuth() {
    const token = getAuthToken();
    if (!token) {
        // Redirect to login if on protected page
        const protectedPages = ['/dashboard/', '/offering/', '/payment/'];
        if (protectedPages.some(page => window.location.pathname.includes(page))) {
            window.location.href = '/login/';
        }
        return false;
    }
    return true;
}

// Logout function
function logout() {
    clearAuthToken();
    window.location.href = '/';
}

// Initialize authentication check on page load
document.addEventListener('DOMContentLoaded', function() {
    // Only check auth on protected pages
    const protectedPages = ['/dashboard/', '/offering/', '/payment/'];
    if (protectedPages.some(page => window.location.pathname.includes(page))) {
        checkAuth();
    }
});