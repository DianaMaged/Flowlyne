const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = 'flowlyne_secret_key_2025'; // In production, use environment variable

// Database setup
const DB_PATH = path.join(__dirname, 'flowlyne.db');
const db = new sqlite3.Database(DB_PATH);

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('../src')); // Serve frontend files from parent directory

// Database initialization
async function initializeDatabase() {
    try {
        // Read and execute schema
        const schemaPath = path.join(__dirname, 'database.sql');
        const schema = fs.readFileSync(schemaPath, 'utf8');
        
        // Execute schema (split by semicolon and run each statement)
        const statements = schema.split(';').filter(stmt => stmt.trim());
        
        for (const statement of statements) {
            if (statement.trim()) {
                await new Promise((resolve, reject) => {
                    db.run(statement, (err) => {
                        if (err) reject(err);
                        else resolve();
                    });
                });
            }
        }
        
        console.log('✅ Database initialized successfully');
    } catch (error) {
        console.error('❌ Error initializing database:', error);
    }
}

// Database helper functions
function dbGet(query, params = []) {
    return new Promise((resolve, reject) => {
        db.get(query, params, (err, row) => {
            if (err) reject(err);
            else resolve(row);
        });
    });
}

function dbAll(query, params = []) {
    return new Promise((resolve, reject) => {
        db.all(query, params, (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });
}

function dbRun(query, params = []) {
    return new Promise((resolve, reject) => {
        db.run(query, params, function(err) {
            if (err) reject(err);
            else resolve({ id: this.lastID, changes: this.changes });
        });
    });
}

// Middleware to verify JWT token
function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    
    if (!token) {
        return res.status(401).json({ error: 'Access token required' });
    }
    
    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ error: 'Invalid token' });
        }
        req.user = user;
        next();
    });
}

// Routes

// Health check
app.get('/api/health', (req, res) => {
    res.json({ status: 'OK', message: 'Flowlyne Backend with SQLite is running' });
});

// User registration
app.post('/api/register', async (req, res) => {
    try {
        const { name, email, password, type, company, services, description, phone, website } = req.body;
        
        // Validation
        if (!name || !email || !password || !type) {
            return res.status(400).json({ error: 'Missing required fields' });
        }
        
        // Check if user already exists
        const existingUser = await dbGet('SELECT id FROM users WHERE email = ?', [email]);
        if (existingUser) {
            return res.status(400).json({ error: 'Email already registered' });
        }
        
        // Hash password
        const hashedPassword = await bcrypt.hash(password, 10);
        const userId = uuidv4();
        
        // Insert user
        await dbRun(`
            INSERT INTO users (id, name, email, password, type, company, phone, website)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        `, [userId, name, email, hashedPassword, type, company || '', phone || '', website || '']);
        
        // If provider, insert service provider details
        if (type === 'provider' && services) {
            const serviceProviderId = uuidv4();
            await dbRun(`
                INSERT INTO service_providers (id, user_id, services, description, hourly_rate, experience_years)
                VALUES (?, ?, ?, ?, ?, ?)
            `, [serviceProviderId, userId, services, description || '', 0, 0]);
        }
        
        // Generate JWT token
        const token = jwt.sign(
            { id: userId, email, type },
            JWT_SECRET,
            { expiresIn: '24h' }
        );
        
        // Get user data without password
        const userData = await dbGet(`
            SELECT u.*, sp.services, sp.description, sp.hourly_rate, sp.rating, sp.total_reviews
            FROM users u
            LEFT JOIN service_providers sp ON u.id = sp.user_id
            WHERE u.id = ?
        `, [userId]);
        
        const { password: _, ...userWithoutPassword } = userData;
        
        res.status(201).json({
            message: 'Registration successful',
            user: userWithoutPassword,
            token
        });
        
    } catch (error) {
        console.error('Registration error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// User login
app.post('/api/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        
        if (!email || !password) {
            return res.status(400).json({ error: 'Email and password required' });
        }
        
        // Get user with service provider data
        const user = await dbGet(`
            SELECT u.*, sp.services, sp.description, sp.hourly_rate, sp.rating, sp.total_reviews
            FROM users u
            LEFT JOIN service_providers sp ON u.id = sp.user_id
            WHERE u.email = ?
        `, [email]);
        
        if (!user) {
            return res.status(400).json({ error: 'Invalid credentials' });
        }
        
        // Verify password
        const isValidPassword = await bcrypt.compare(password, user.password);
        if (!isValidPassword) {
            return res.status(400).json({ error: 'Invalid credentials' });
        }
        
        // Generate JWT token
        const token = jwt.sign(
            { id: user.id, email: user.email, type: user.type },
            JWT_SECRET,
            { expiresIn: '24h' }
        );
        
        // Return user data without password
        const { password: _, ...userWithoutPassword } = user;
        
        res.json({
            message: 'Login successful',
            user: userWithoutPassword,
            token
        });
        
    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get all service providers
app.get('/api/providers', async (req, res) => {
    try {
        const providers = await dbAll(`
            SELECT 
                u.id, u.name, u.email, u.company, u.phone, u.location, u.website, u.is_verified,
                sp.services, sp.description, sp.hourly_rate, sp.experience_years, 
                sp.rating, sp.total_reviews, sp.completed_projects, sp.availability
            FROM users u
            INNER JOIN service_providers sp ON u.id = sp.user_id
            WHERE u.type = 'provider'
            ORDER BY sp.rating DESC, sp.total_reviews DESC
        `);
        
        res.json(providers);
    } catch (error) {
        console.error('Error fetching providers:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Search providers
app.get('/api/providers/search', async (req, res) => {
    try {
        const { q } = req.query;
        
        if (!q) {
            return res.status(400).json({ error: 'Search query required' });
        }
        
        const searchTerm = `%${q.toLowerCase()}%`;
        
        const providers = await dbAll(`
            SELECT 
                u.id, u.name, u.email, u.company, u.phone, u.location, u.website, u.is_verified,
                sp.services, sp.description, sp.hourly_rate, sp.experience_years, 
                sp.rating, sp.total_reviews, sp.completed_projects, sp.availability
            FROM users u
            INNER JOIN service_providers sp ON u.id = sp.user_id
            WHERE u.type = 'provider' 
            AND (LOWER(sp.services) LIKE ? 
                 OR LOWER(u.name) LIKE ? 
                 OR LOWER(sp.description) LIKE ?
                 OR LOWER(u.company) LIKE ?)
            ORDER BY sp.rating DESC
        `, [searchTerm, searchTerm, searchTerm, searchTerm]);
        
        res.json(providers);
    } catch (error) {
        console.error('Error searching providers:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Send message (contact provider)
app.post('/api/messages', authenticateToken, async (req, res) => {
    try {
        const { receiverEmail, subject, message } = req.body;
        
        if (!receiverEmail || !message) {
            return res.status(400).json({ error: 'Receiver email and message required' });
        }
        
        // Get receiver user
        const receiver = await dbGet('SELECT id FROM users WHERE email = ?', [receiverEmail]);
        if (!receiver) {
            return res.status(404).json({ error: 'Receiver not found' });
        }
        
        const messageId = uuidv4();
        
        await dbRun(`
            INSERT INTO messages (id, sender_id, receiver_id, subject, message)
            VALUES (?, ?, ?, ?, ?)
        `, [messageId, req.user.id, receiver.id, subject || 'Contact from Flowlyne', message]);
        
        res.status(201).json({
            message: 'Message sent successfully',
            id: messageId
        });
        
    } catch (error) {
        console.error('Error sending message:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get platform statistics
app.get('/api/stats', async (req, res) => {
    try {
        const totalUsers = await dbGet('SELECT COUNT(*) as count FROM users');
        const serviceProviders = await dbGet('SELECT COUNT(*) as count FROM users WHERE type = "provider"');
        const companies = await dbGet('SELECT COUNT(*) as count FROM users WHERE type = "company"');
        const totalMessages = await dbGet('SELECT COUNT(*) as count FROM messages');
        const totalProjects = await dbGet('SELECT COUNT(*) as count FROM projects');
        
        const stats = {
            totalUsers: totalUsers.count,
            serviceProviders: serviceProviders.count,
            companies: companies.count,
            totalMessages: totalMessages.count,
            totalProjects: totalProjects?.count || 0
        };
        
        res.json(stats);
    } catch (error) {
        console.error('Error fetching stats:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get service categories
app.get('/api/categories', async (req, res) => {
    try {
        const categories = await dbAll('SELECT * FROM service_categories ORDER BY name');
        res.json(categories);
    } catch (error) {
        console.error('Error fetching categories:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get projects (for companies to post and providers to browse)
app.get('/api/projects', async (req, res) => {
    try {
        const projects = await dbAll(`
            SELECT 
                p.*, 
                u.name as company_name, 
                u.company as company_business,
                sc.name as category_name
            FROM projects p
            INNER JOIN users u ON p.company_id = u.id
            LEFT JOIN service_categories sc ON p.category_id = sc.id
            WHERE p.status = 'open'
            ORDER BY p.created_at DESC
        `);
        
        res.json(projects);
    } catch (error) {
        console.error('Error fetching projects:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Create project (companies only)
app.post('/api/projects', authenticateToken, async (req, res) => {
    try {
        // Check if user is a company
        if (req.user.type !== 'company') {
            return res.status(403).json({ error: 'Only companies can create projects' });
        }
        
        const { title, description, budget_min, budget_max, deadline, category_id, skills_required } = req.body;
        
        if (!title || !description) {
            return res.status(400).json({ error: 'Title and description required' });
        }
        
        const projectId = uuidv4();
        
        await dbRun(`
            INSERT INTO projects (id, company_id, title, description, budget_min, budget_max, deadline, category_id, skills_required)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        `, [projectId, req.user.id, title, description, budget_min || 0, budget_max || 0, deadline, category_id, JSON.stringify(skills_required || [])]);
        
        res.status(201).json({
            message: 'Project created successfully',
            id: projectId
        });
        
    } catch (error) {
        console.error('Error creating project:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Serve frontend files
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../src', 'index.html'));
});

// Initialize database and start server
initializeDatabase().then(() => {
    app.listen(PORT, () => {
        console.log('🚀 Flowlyne Backend with SQLite is running');
        console.log(`📊 Frontend: http://localhost:${PORT}`);
        console.log(`🔗 API: http://localhost:${PORT}/api/`);
        console.log(`💾 Database: ${DB_PATH}`);
    });
}).catch(error => {
    console.error('Failed to start server:', error);
    process.exit(1);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down gracefully...');
    db.close((err) => {
        if (err) {
            console.error('Error closing database:', err);
        } else {
            console.log('✅ Database connection closed');
        }
        process.exit(0);
    });
});