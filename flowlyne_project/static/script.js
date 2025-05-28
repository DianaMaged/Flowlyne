// Global config
const API_BASE_URL = 'http://localhost:3000/api';

// Token helpers
function setAuthToken(token) {
    localStorage.setItem('flowlyne_access', token);
}

function getAuthToken() {
    return localStorage.getItem('flowlyne_access');
}

function clearAuthToken() {
    localStorage.removeItem('flowlyne_access');
    localStorage.removeItem('flowlyne_refresh');
}

// Generic API call
async function apiRequest(endpoint, options = {}) {
    const token = getAuthToken();
    const headers = options.headers || { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'API error');
    }

    return await response.json();
}

// Login
async function handleLogin(event) {
    event.preventDefault();

    const loginData = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };

    try {
        const response = await apiRequest('/token/', {
            method: 'POST',
            body: JSON.stringify(loginData)
        });

        localStorage.setItem('flowlyne_access', response.access);
        localStorage.setItem('flowlyne_refresh', response.refresh);
        window.location.href = 'dashboard.html';
    } catch (error) {
        alert('Login failed. Please check your credentials.');
    }
}

// Register
async function handleRegister(event) {
    event.preventDefault();

    const registerData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        confirm_password: document.getElementById('confirm_password').value
    };

    try {
        const response = await apiRequest('/register/', {
            method: 'POST',
            body: JSON.stringify(registerData)
        });

        setAuthToken(response.token);
        window.location.href = 'dashboard.html';
    } catch (error) {
        alert('Registration failed. Please check your data.');
    }
}

// Logout
function logout() {
    clearAuthToken();
    window.location.href = 'index.html';
}

// Navbar update
function updateNavigation() {
    const navLinks = document.querySelector('.nav-links');
    const token = getAuthToken();

    if (!navLinks) return;

    if (token) {
        const currentUser = JSON.parse(localStorage.getItem('currentUser')) || { name: 'User' };
        navLinks.innerHTML = `
            <a href="index.html">Home</a>
            <a href="about.html">About</a>
            <a href="services.html">Find Services</a>
            <a href="dashboard.html">Dashboard</a>
            <a href="#" onclick="logout()">Logout (${currentUser.name})</a>
        `;
    } else {
        navLinks.innerHTML = `
            <a href="index.html">Home</a>
            <a href="about.html">About</a>
            <a href="services.html">Find Services</a>
            <a href="login.html">Login</a>
            <a href="register.html">Register</a>
        `;
    }
}

document.addEventListener('DOMContentLoaded', updateNavigation);
