-- Flowlyne Database Schema
-- SQLite database schema for the B2B platform

-- Users table (companies and service providers)
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('company', 'provider')),
    company TEXT,
    phone TEXT,
    location TEXT DEFAULT 'Egypt',
    website TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT FALSE,
    profile_image TEXT
);

-- Service providers table (extends users for providers)
CREATE TABLE IF NOT EXISTS service_providers (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    services TEXT NOT NULL,
    description TEXT,
    hourly_rate DECIMAL(10,2),
    experience_years INTEGER,
    portfolio_url TEXT,
    skills TEXT, -- JSON array of skills
    availability TEXT DEFAULT 'available',
    rating DECIMAL(3,2) DEFAULT 0.00,
    total_reviews INTEGER DEFAULT 0,
    completed_projects INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Service categories table
CREATE TABLE IF NOT EXISTS service_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    icon TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Messages/Contact table
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    sender_id TEXT NOT NULL,
    receiver_id TEXT NOT NULL,
    subject TEXT,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Projects/Job postings table
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    budget_min DECIMAL(10,2),
    budget_max DECIMAL(10,2),
    deadline DATE,
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'completed', 'cancelled')),
    category_id INTEGER,
    skills_required TEXT, -- JSON array
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES service_categories(id)
);

-- Proposals table (service providers bidding on projects)
CREATE TABLE IF NOT EXISTS proposals (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    proposal_text TEXT NOT NULL,
    quoted_price DECIMAL(10,2) NOT NULL,
    estimated_duration TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (provider_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(project_id, provider_id)
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id TEXT PRIMARY KEY,
    reviewer_id TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    project_id TEXT,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (provider_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
);

-- Insert initial service categories
INSERT OR IGNORE INTO service_categories (name, description, icon) VALUES
('Web Development', 'Website and web application development', '💻'),
('Mobile App Development', 'iOS and Android mobile applications', '📱'),
('Digital Marketing', 'SEO, social media, and online marketing', '📈'),
('Graphic Design', 'Logo design, branding, and visual content', '🎨'),
('Content Writing', 'Blog posts, copywriting, and content creation', '✍️'),
('Accounting & Finance', 'Bookkeeping, financial planning, and tax services', '💰'),
('Business Consulting', 'Strategy, operations, and management consulting', '🎯'),
('Legal Services', 'Business law, contracts, and legal consultation', '⚖️'),
('Translation Services', 'Document translation and localization', '🌍'),
('Video Production', 'Video editing, animation, and multimedia content', '🎬');

-- Insert sample data for testing
INSERT OR IGNORE INTO users (id, name, email, password, type, company, phone, location, is_verified) VALUES
('demo-company-1', 'Ahmed Enterprises', 'ahmed@demo.com', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'company', 'Ahmed Trading Co.', '+20-100-123-4567', 'Cairo, Egypt', TRUE),
('demo-provider-1', 'Mohamed Hassan', 'mohamed@webdev.com', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'provider', 'Hassan Web Solutions', '+20-101-234-5678', 'Giza, Egypt', TRUE),
('demo-provider-2', 'Fatma Ali', 'fatma@design.com', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'provider', 'Creative Studio Egypt', '+20-102-345-6789', 'Alexandria, Egypt', TRUE),
('demo-provider-3', 'Omar Khaled', 'omar@marketing.com', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'provider', 'Digital Marketing Pro', '+20-103-456-7890', 'Cairo, Egypt', TRUE);

-- Insert service provider details
INSERT OR IGNORE INTO service_providers (id, user_id, services, description, hourly_rate, experience_years, skills, rating, total_reviews, completed_projects) VALUES
('sp-1', 'demo-provider-1', 'Web Development', 'Expert full-stack developer specializing in React, Node.js, and modern web technologies. I help Egyptian businesses build professional websites and web applications.', 25.00, 5, '["React", "Node.js", "JavaScript", "HTML/CSS", "MongoDB"]', 4.8, 12, 28),
('sp-2', 'demo-provider-2', 'Graphic Design', 'Professional graphic designer with expertise in branding, logo design, and marketing materials. I create stunning visuals that help Egyptian businesses stand out.', 20.00, 3, '["Adobe Photoshop", "Illustrator", "Branding", "Logo Design", "Print Design"]', 4.9, 8, 15),
('sp-3', 'demo-provider-3', 'Digital Marketing', 'Digital marketing specialist helping Egyptian businesses grow online through SEO, social media marketing, and Google Ads campaigns.', 18.00, 4, '["SEO", "Google Ads", "Facebook Ads", "Content Marketing", "Analytics"]', 4.7, 15, 22);

-- Insert sample projects
INSERT OR IGNORE INTO projects (id, company_id, title, description, budget_min, budget_max, deadline, category_id, skills_required) VALUES
('proj-1', 'demo-company-1', 'E-commerce Website Development', 'Need a modern e-commerce website for selling traditional Egyptian products online. Should include payment gateway integration and mobile responsive design.', 1500.00, 3000.00, '2025-07-15', 1, '["React", "E-commerce", "Payment Integration"]'),
('proj-2', 'demo-company-1', 'Company Logo and Branding', 'Looking for a professional logo and complete branding package for our new Egyptian restaurant chain.', 500.00, 1000.00, '2025-06-30', 4, '["Logo Design", "Branding", "Restaurant Design"]');

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_type ON users(type);
CREATE INDEX IF NOT EXISTS idx_service_providers_rating ON service_providers(rating DESC);
CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_reviews_provider ON reviews(provider_id);