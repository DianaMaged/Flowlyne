// Simple data storage (in a real app, this would be a database)
let users = JSON.parse(localStorage.getItem('flowlyne_users')) || [];
let currentUser = JSON.parse(localStorage.getItem('flowlyne_current_user')) || null;

// Save data to localStorage
function saveData() {
    localStorage.setItem('flowlyne_users', JSON.stringify(users));
    localStorage.setItem('flowlyne_current_user', JSON.stringify(currentUser));
}

// Check if user is logged in and update nav
function updateNavigation() {
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
    currentUser = null;
    localStorage.removeItem('flowlyne_current_user');
    window.location.href = 'index.html';
}

// Registration form handler
function handleRegistration(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const userData = {
        id: Date.now(),
        name: formData.get('name'),
        email: formData.get('email'),
        password: formData.get('password'),
        type: formData.get('userType'),
        company: formData.get('company'),
        services: formData.get('services'),
        description: formData.get('description'),
        createdAt: new Date().toISOString()
    };
    
    // Check if email already exists
    if (users.find(user => user.email === userData.email)) {
        alert('Email already registered!');
        return;
    }
    
    users.push(userData);
    currentUser = userData;
    saveData();
    
    alert('Registration successful!');
    window.location.href = 'dashboard.html';
}

// Login form handler
function handleLogin(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const email = formData.get('email');
    const password = formData.get('password');
    
    const user = users.find(u => u.email === email && u.password === password);
    
    if (user) {
        currentUser = user;
        saveData();
        alert('Login successful!');
        window.location.href = 'dashboard.html';
    } else {
        alert('Invalid email or password!');
    }
}

// Display service providers
function displayServiceProviders() {
    const providers = users.filter(user => user.type === 'provider');
    const container = document.getElementById('providers-container');
    
    if (!container) return;
    
    if (providers.length === 0) {
        container.innerHTML = '<p>No service providers registered yet.</p>';
        return;
    }
    
    container.innerHTML = providers.map(provider => `
        <div class="provider-card">
            <h3>${provider.name}</h3>
            <p><strong>Company:</strong> ${provider.company || 'Not specified'}</p>
            <p><strong>Services:</strong> ${provider.services || 'Not specified'}</p>
            <p><strong>Description:</strong> ${provider.description || 'No description available'}</p>
            <button onclick="contactProvider('${provider.email}')" class="btn btn-primary">Contact</button>
        </div>
    `).join('');
}

// Contact provider function
function contactProvider(email) {
    if (!currentUser) {
        alert('Please login to contact service providers');
        window.location.href = 'login.html';
        return;
    }
    
    const message = prompt('Enter your message:');
    if (message) {
        alert(`Message sent to ${email}: "${message}"\n\nNote: In a real app, this would send an actual email.`);
    }
}

// Search functionality
function searchProviders() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const providers = users.filter(user => 
        user.type === 'provider' && 
        (user.services?.toLowerCase().includes(searchTerm) || 
         user.name.toLowerCase().includes(searchTerm) ||
         user.description?.toLowerCase().includes(searchTerm))
    );
    
    const container = document.getElementById('providers-container');
    if (!container) return;
    
    if (providers.length === 0) {
        container.innerHTML = '<p>No providers found matching your search.</p>';
        return;
    }
    
    container.innerHTML = providers.map(provider => `
        <div class="provider-card">
            <h3>${provider.name}</h3>
            <p><strong>Company:</strong> ${provider.company || 'Not specified'}</p>
            <p><strong>Services:</strong> ${provider.services || 'Not specified'}</p>
            <p><strong>Description:</strong> ${provider.description || 'No description available'}</p>
            <button onclick="contactProvider('${provider.email}')" class="btn btn-primary">Contact</button>
        </div>
    `).join('');
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
});

// Toggle form fields based on user type
function toggleUserTypeFields() {
    const userType = document.getElementById('userType').value;
    const providerFields = document.getElementById('provider-fields');
    
    if (providerFields) {
        if (userType === 'provider') {
            providerFields.style.display = 'block';
        } else {
            providerFields.style.display = 'none';
        }
    }
}