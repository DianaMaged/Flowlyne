// Fixed JavaScript - No localStorage, relies on Django sessions

// CSRF Token helper for AJAX requests
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

// Generic API request helper
async function apiRequest(endpoint, options = {}) {
    const url = `/api${endpoint}`;
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        credentials: 'include', // Include session cookies
    };

    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        }
    };

    const response = await fetch(url, mergedOptions);
    
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
}

// Login function - for AJAX login (if you want to keep it)
async function handleLogin(event) {
    event.preventDefault();

    const loginData = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };

    try {
        const response = await apiRequest('/login/', {
            method: 'POST',
            body: JSON.stringify(loginData)
        });

        // Success! Django session is now active
        // Redirect to dashboard
        window.location.href = '/dashboard/';
    } catch (error) {
        console.error('Login error:', error);
        // Display error message
        const errorDiv = document.getElementById('error-message');
        if (errorDiv) {
            errorDiv.textContent = error.message;
            errorDiv.style.display = 'block';
        } else {
            alert('Login failed: ' + error.message);
        }
    }
}

// Register function - for AJAX registration (if you want to keep it)
async function handleRegister(event) {
    event.preventDefault();

    const registerData = {
        company_name: document.getElementById('company_name').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        description: document.getElementById('description').value
    };

    try {
        const response = await apiRequest('/register/', {
            method: 'POST',
            body: JSON.stringify(registerData)
        });

        // Success! Django session is now active
        // Redirect to dashboard
        window.location.href = '/dashboard/';
    } catch (error) {
        console.error('Registration error:', error);
        // Display error message
        const errorDiv = document.getElementById('error-message');
        if (errorDiv) {
            errorDiv.textContent = error.message;
            errorDiv.style.display = 'block';
        } else {
            alert('Registration failed: ' + error.message);
        }
    }
}

// Logout function - Simply redirect to Django logout view
function logout() {
    window.location.href = '/logout/';
}

// Services functions
async function loadServices() {
    try {
        const response = await apiRequest('/services/all/');
        displayServices(response.services);
    } catch (error) {
        console.error('Error loading services:', error);
    }
}

function displayServices(services) {
    const container = document.getElementById('services-container');
    if (!container) return;

    container.innerHTML = '';

    if (!services || services.length === 0) {
        container.innerHTML = '<div class="col-12"><p class="text-center">No services found.</p></div>';
        return;
    }

    services.forEach(service => {
        const serviceCard = createServiceCard(service);
        container.appendChild(serviceCard);
    });
}

function createServiceCard(service) {
    const col = document.createElement('div');
    col.className = 'col-md-6 col-lg-4 mb-4';

    col.innerHTML = `
        <div class="card h-100 service-card">
            <div class="card-body">
                <h5 class="card-title">${escapeHtml(service.service_name)}</h5>
                <p class="card-text">${escapeHtml(service.description || 'No description available')}</p>
                <p class="text-muted">
                    <strong>Company:</strong> ${escapeHtml(service.company_name)}<br>
                    <strong>Category:</strong> ${escapeHtml(service.category_name)}<br>
                    <strong>Price:</strong> $${service.price}
                </p>
            </div>
            <div class="card-footer">
                <button class="btn btn-primary btn-sm" onclick="contactCompany(${service.company_id})">
                    Contact Company
                </button>
            </div>
        </div>
    `;

    return col;
}

// Companies functions
async function loadCompanies() {
    try {
        const response = await apiRequest('/companies/');
        displayCompanies(response.companies);
    } catch (error) {
        console.error('Error loading companies:', error);
    }
}

function displayCompanies(companies) {
    const container = document.getElementById('companies-container');
    if (!container) return;

    container.innerHTML = '';

    if (!companies || companies.length === 0) {
        container.innerHTML = '<div class="col-12"><p class="text-center">No companies found.</p></div>';
        return;
    }

    companies.forEach(company => {
        const companyCard = createCompanyCard(company);
        container.appendChild(companyCard);
    });
}

function createCompanyCard(company) {
    const col = document.createElement('div');
    col.className = 'col-md-6 col-lg-4 mb-4';

    col.innerHTML = `
        <div class="card h-100 company-card">
            <div class="card-body">
                <h5 class="card-title">${escapeHtml(company.company_name)}</h5>
                <p class="card-text">${escapeHtml(company.description || 'No description available')}</p>
                <p class="text-muted">
                    <strong>Location:</strong> ${escapeHtml(company.city)}, ${escapeHtml(company.country)}<br>
                    <strong>Plan:</strong> ${escapeHtml(company.current_plan)}<br>
                    ${company.is_verified ? '<span class="badge bg-success">Verified</span>' : ''}
                </p>
            </div>
            <div class="card-footer">
                <button class="btn btn-primary btn-sm" onclick="viewCompanyDetails(${company.company_id})">
                    View Details
                </button>
            </div>
        </div>
    `;

    return col;
}

// Dashboard functions (for authenticated users)
async function loadDashboardStats() {
    try {
        const response = await apiRequest('/stats/');
        displayStats(response.stats);
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

function displayStats(stats) {
    // Update stats on dashboard
    const elements = {
        'total-services': stats.total_services,
        'active-services': stats.active_services,
        'total-reviews': stats.total_reviews,
        'average-rating': stats.average_rating.toFixed(1),
        'current-plan': stats.current_plan,
    };

    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
}

// Company services functions
async function loadCompanyServices() {
    try {
        const response = await apiRequest('/services/');
        displayCompanyServices(response.services);
    } catch (error) {
        console.error('Error loading company services:', error);
    }
}

function displayCompanyServices(services) {
    const container = document.getElementById('company-services-container');
    if (!container) return;

    container.innerHTML = '';

    if (!services || services.length === 0) {
        container.innerHTML = '<div class="col-12"><p class="text-center">No services found. <a href="#" onclick="showCreateServiceForm()">Create your first service</a></p></div>';
        return;
    }

    services.forEach(service => {
        const serviceCard = createCompanyServiceCard(service);
        container.appendChild(serviceCard);
    });
}

function createCompanyServiceCard(service) {
    const col = document.createElement('div');
    col.className = 'col-md-6 col-lg-4 mb-4';

    col.innerHTML = `
        <div class="card h-100">
            <div class="card-body">
                <h5 class="card-title">${escapeHtml(service.service_name)}</h5>
                <p class="card-text">${escapeHtml(service.description || 'No description available')}</p>
                <p class="text-muted">
                    <strong>Category:</strong> ${escapeHtml(service.category_name)}<br>
                    <strong>Price:</strong> $${service.price}<br>
                    <strong>Status:</strong> ${service.is_active ? '<span class="badge bg-success">Active</span>' : '<span class="badge bg-secondary">Inactive</span>'}
                </p>
            </div>
            <div class="card-footer">
                <button class="btn btn-primary btn-sm" onclick="editService(${service.service_id})">
                    Edit
                </button>
                <button class="btn btn-danger btn-sm" onclick="deleteService(${service.service_id})">
                    Delete
                </button>
            </div>
        </div>
    `;

    return col;
}

// Utility functions
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text ? text.replace(/[&<>"']/g, m => map[m]) : '';
}

function contactCompany(companyId) {
    // Implement contact functionality
    alert(`Contact functionality for company ${companyId} - implement as needed`);
}

function viewCompanyDetails(companyId) {
    // Implement company details view
    window.location.href = `/companies/${companyId}/`;
}

function showCreateServiceForm() {
    // Implement service creation form
    alert('Service creation form - implement as needed');
}

function editService(serviceId) {
    // Implement service editing
    alert(`Edit service ${serviceId} - implement as needed`);
}

function deleteService(serviceId) {
    if (confirm('Are you sure you want to delete this service?')) {
        // Implement service deletion
        alert(`Delete service ${serviceId} - implement as needed`);
    }
}

// Initialize page-specific functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check which page we're on and load appropriate content
    const path = window.location.pathname;
    
    if (path.includes('/services/')) {
        loadServices();
        loadCompanies();
    } else if (path.includes('/dashboard/')) {
        loadDashboardStats();
        loadCompanyServices();
    } else if (path.includes('/offering/')) {
        loadCompanyServices();
    }
    
    // Attach form handlers if forms exist
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
});