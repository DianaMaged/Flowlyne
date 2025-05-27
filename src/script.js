// Backend API configuration
const API_BASE_URL = 'http://localhost:3000/api';

// Get auth token from localStorage
function getAuthToken() {
    return localStorage.getItem('flowlyne_token');
}

// Set auth token
function setAuthToken(token) {
    localStorage.setItem('flowlyne_token', token);
}

// Remove auth token
function removeAuthToken() {
    localStorage.removeItem('flowlyne_token');
    localStorage.removeItem('flowlyne_current_user');
}

// Get current user from localStorage
function getCurrentUser() {
    return JSON.parse(localStorage.getItem('flowlyne_current_user'));
}

// Set current user
function setCurrentUser(user) {
    localStorage.setItem('flowlyne_current_user', JSON.stringify(user));
}

// Make API request with authentication
async function apiRequest(endpoint, options = {}) {
    const token = getAuthToken();
    const defaultHeaders = {
        'Content-Type': 'application/json',
    };
    
    if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        headers: defaultHeaders,
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Check if user is logged in and update nav
function updateNavigation() {
    const currentUser = getCurrentUser();
    const navLinks = document.querySelector('.nav-links');
    
    if (currentUser && navLinks) {
        navLinks.innerHTML = `
            <a href="index.html">Home</a>
            <a href="services.html">Find Services</a>
            <a href="dashboard.html">Dashboard</a>
            <a href="#" onclick="logout()">Logout (${currentUser.name})</a>
        `;
    }
}

// Logout function
function logout() {
    removeAuthToken();
    alert('Logged out successfully');
    window.location.href = 'index.html';
}

// Registration form handler
async function handleRegistration(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const userData = {
        name: formData.get('name'),
        email: formData.get('email'),
        password: formData.get('password'),
        type: formData.get('userType'),
        company: formData.get('company') || '',
        services: formData.get('services') || '',
        description: formData.get('description') || ''
    };
    
    try {
        // Show loading state
        const submitBtn = event.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Creating Account...';
        submitBtn.disabled = true;
        
        const response = await apiRequest('/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        
        // Store token and user data
        setAuthToken(response.token);
        setCurrentUser(response.user);
        
        alert('Registration successful!');
        window.location.href = 'dashboard.html';
        
    } catch (error) {
        alert(`Registration failed: ${error.message}`);
        
        // Reset button
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.textContent = 'Create Account';
        submitBtn.disabled = false;
    }
}

// Login form handler
async function handleLogin(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const loginData = {
        email: formData.get('email'),
        password: formData.get('password')
    };
    
    try {
        // Show loading state
        const submitBtn = event.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Logging in...';
        submitBtn.disabled = true;
        
        const response = await apiRequest('/login', {
            method: 'POST',
            body: JSON.stringify(loginData)
        });
        
        // Store token and user data
        setAuthToken(response.token);
        setCurrentUser(response.user);
        
        alert('Login successful!');
        window.location.href = 'dashboard.html';
        
    } catch (error) {
        alert(`Login failed: ${error.message}`);
        
        // Reset button
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.textContent = 'Login';
        submitBtn.disabled = false;
    }
}

// Display service providers
async function displayServiceProviders() {
    const container = document.getElementById('providers-container');
    
    if (!container) return;
    
    try {
        // Show loading state
        container.innerHTML = '<div style="text-align: center; padding: 2rem;"><p>Loading service providers...</p></div>';
        
        const providers = await apiRequest('/providers');
        
        if (providers.length === 0) {
            container.innerHTML = '<div class="no-results"><h3>No service providers available</h3><p>Be the first to join as a service provider!</p></div>';
            return;
        }
        
        container.innerHTML = providers.map(provider => `
            <div class="provider-card">
                <div class="provider-header">
                    <div class="provider-info">
                        <h3>${provider.name}</h3>
                        <div class="provider-meta">
                            <span>${provider.services || 'General Services'}</span>
                            <span>${provider.company || 'Independent'}</span>
                        </div>
                    </div>
                </div>
                <div class="provider-description">
                    ${provider.description || 'Professional service provider ready to help your business grow.'}
                </div>
                <button onclick="contactProvider('${provider.email}')" class="contact-btn">
                    Contact Provider
                </button>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading providers:', error);
        container.innerHTML = '<div class="no-results"><h3>Error loading providers</h3><p>Please try again later.</p></div>';
    }
}

// Contact provider function
async function contactProvider(email) {
    const currentUser = getCurrentUser();
    
    if (!currentUser) {
        alert('Please login to contact service providers');
        window.location.href = 'login.html';
        return;
    }
    
    const message = prompt('Enter your message:');
    if (!message) return;
    
    try {
        await apiRequest('/messages', {
            method: 'POST',
            body: JSON.stringify({
                receiverEmail: email,
                message: message
            })
        });
        
        alert('Message sent successfully! The service provider will get back to you soon.');
        
    } catch (error) {
        alert(`Failed to send message: ${error.message}`);
    }
}

// Search functionality
async function searchProviders() {
    const searchTerm = document.getElementById('search-input').value.trim();
    const container = document.getElementById('providers-container');
    
    if (!container) return;
    
    if (!searchTerm) {
        displayServiceProviders();
        return;
    }
    
    try {
        // Show loading state
        container.innerHTML = '<div style="text-align: center; padding: 2rem;"><p>Searching...</p></div>';
        
        const providers = await apiRequest(`/providers/search?q=${encodeURIComponent(searchTerm)}`);
        
        if (providers.length === 0) {
            container.innerHTML = `
                <div class="no-results">
                    <h3>No providers found</h3>
                    <p>No providers match "${searchTerm}". Try a different search term.</p>
                    <button onclick="displayServiceProviders()" class="btn btn-secondary" style="margin-top: 1rem;">
                        Show All Providers
                    </button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = providers.map(provider => `
            <div class="provider-card">
                <div class="provider-header">
                    <div class="provider-info">
                        <h3>${provider.name}</h3>
                        <div class="provider-meta">
                            <span>${provider.services || 'General Services'}</span>
                            <span>${provider.company || 'Independent'}</span>
                        </div>
                    </div>
                </div>
                <div class="provider-description">
                    ${provider.description || 'Professional service provider ready to help your business grow.'}
                </div>
                <button onclick="contactProvider('${provider.email}')" class="contact-btn">
                    Contact Provider
                </button>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Search error:', error);
        container.innerHTML = '<div class="no-results"><h3>Search failed</h3><p>Please try again.</p></div>';
    }
}

// Load dashboard data
async function loadDashboard() {
    const currentUser = getCurrentUser();
    
    if (!currentUser) {
        alert('Please login to access your dashboard');
        window.location.href = 'login.html';
        return;
    }
    
    try {
        // Load platform statistics
        const stats = await apiRequest('/stats');
        
        // Update welcome message
        const welcomeElement = document.getElementById('welcome-message');
        if (welcomeElement) {
            welcomeElement.textContent = `Welcome back, ${currentUser.name}!`;
        }
        
        // Update stats
        const elements = {
            'total-users': stats.totalUsers,
            'service-providers': stats.serviceProviders,
            'companies': stats.companies
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        });
        
        // Format member since date
        const memberDate = new Date(currentUser.createdAt);
        const memberSinceElement = document.getElementById('member-since');
        if (memberSinceElement) {
            memberSinceElement.textContent = memberDate.toLocaleDateString();
        }
        
        // Update user type badge
        const badge = document.getElementById('user-type-badge');
        if (badge) {
            badge.textContent = currentUser.type === 'provider' ? 'Service Provider' : 'Company';
            badge.style.background = currentUser.type === 'provider' ? '#e74c3c' : '#3498db';
        }
        
        // Populate profile information
        const profileInfo = document.getElementById('profile-info');
        if (profileInfo) {
            profileInfo.innerHTML = `
                <div class="info-item">
                    <div class="info-label">Full Name</div>
                    <div class="info-value">${currentUser.name}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Email Address</div>
                    <div class="info-value">${currentUser.email}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Company</div>
                    <div class="info-value">${currentUser.company || 'Not specified'}</div>
                </div>
                ${currentUser.type === 'provider' ? `
                <div class="info-item">
                    <div class="info-label">Services Offered</div>
                    <div class="info-value">${currentUser.services || 'Not specified'}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Description</div>
                    <div class="info-value">${currentUser.description || 'No description provided'}</div>
                </div>
                ` : ''}
            `;
        }
        
    } catch (error) {
        console.error('Dashboard error:', error);
        alert('Error loading dashboard data');
    }
}

// Toggle form fields based on user type
function toggleUserTypeFields() {
    const userType = document.getElementById('userType')?.value;
    const providerFields = document.getElementById('provider-fields');
    
    if (providerFields) {
        if (userType === 'provider') {
            providerFields.style.display = 'block';
        } else {
            providerFields.style.display = 'none';
        }
    }
}

// Demo message for unimplemented features
function showDemoMessage() {
    alert('This is a demo feature. In a full application, this would provide complete functionality.');
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    updateNavigation();
    
    // Set user type from URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    const userType = urlParams.get('type');
    if (userType) {
        const userTypeSelect = document.getElementById('userType');
        if (userTypeSelect) {
            userTypeSelect.value = userType;
            toggleUserTypeFields();
        }
    }
    
    // Initialize page-specific functionality
    const currentPage = window.location.pathname.split('/').pop();
    
    if (currentPage === 'services.html') {
        displayServiceProviders();
        
        // Enable search on Enter key
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchProviders();
                }
            });
        }
    }
    
    if (currentPage === 'dashboard.html') {
        loadDashboard();
    }
});
