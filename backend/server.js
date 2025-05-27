const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = 'flowlyne_secret_key_2025'; // In production, use environment variable

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('../src')); // Serve frontend files from parent directory

// Database file paths
const USERS_FILE = path.join(__dirname, 'data', 'users.json');
const MESSAGES_FILE = path.join(__dirname, 'data', 'messages.json');

// Initialize data directory
async function initializeData() {
    try {
        await fs.mkdir('data', { recursive: true });
        
        // Initialize users file if it doesn't exist
        try {
            await fs.access(USERS_FILE);
        } catch {
            const initialUsers = [
                {
                    id: uuidv4(),
                    name: 'Demo Company',
                    email: 'company@demo.com',
                    password: await bcrypt.hash('password123', 10),
                    type: 'company',
                    company: 'Demo Corp',
                    createdAt: new Date().toISOString()
                },
                {
                    id: uuidv4(),
                    name: 'Demo Provider',
                    email: 'provider@demo.com',
                    password: await bcrypt.hash('password123', 10),
                    type: 'provider',
                    company: 'Web Solutions Pro',
                    services: 'Web Development',
                    description: 'Professional web development services with 5+ years experience in React, Node.js, and modern web technologies.',
                    createdAt: new Date().toISOString()
                },
                {
                    id: uuidv4(),
                    name: 'Ahmed Hassan',
                    email: 'ahmed@webdev.com',
                    password: await bcrypt.hash('password123', 10),
                    type: 'provider',
                    company: 'Hassan Digital',
                    services: 'Digital Marketing',
                    description: 'Expert in social media marketing, SEO, and Google Ads with 3+ years helping Egyptian businesses grow online.',
                    createdAt: new Date().toISOString()
                },
                {
                    id: uuidv4(),
                    name: 'Fatma Ali',
                    email: 'fatma@designs.com',
                    password: await bcrypt.hash('password123', 10),
                    type: 'provider',
                    company: 'Creative Designs Co',
                    services: 'Graphic Design',
                    description: 'Professional graphic designer specializing in branding, logos, and marketing materials for startups and small businesses.',
                    createdAt: new Date().toISOString()
                }
            ];
            await fs.writeFile(USERS_FILE, JSON.stringify(initialUsers, null, 2));
        }
        
        // Initialize messages file if it doesn't exist
        try {
            await fs.access(MESSAGES_FILE);
        } catch {
            await fs.writeFile(MESSAGES_FILE, JSON.stringify([], null, 2));
        }
        
        console.log('Database initialized successfully');
    } catch (error) {
        console.error('Error initializing database:', error);
    }
}

// Helper functions for database operations
async function readUsers() {
    try {
        const data = await fs.readFile(USERS_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        console.error('Error reading users:', error);
        return [];
    }
}

async function writeUsers(users) {
    try {
        await fs.writeFile(USERS_FILE, JSON.stringify(users, null, 2));
    } catch (error) {
        console.error('Error writing users:', error);
    }
}

async function readMessages() {
    try {
        const data = await fs.readFile(MESSAGES_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        console.error('Error reading messages:', error);
        return [];
    }
}

async function writeMessages(messages) {
    try {
        await fs.writeFile(MESSAGES_FILE, JSON.stringify(messages, null, 2));
    } catch (error) {
        console.error('Error writing messages:', error);
    }
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
    res.json({ status: 'OK', message: 'Flowlyne Backend is running' });
});

// User registration
app.post('/api/register', async (req, res) => {
    try {
        const { name, email, password, type, company, services, description } = req.body;
        
        // Validation
        if (!name || !email || !password || !type) {
            return res.status(400).json({ error: 'Missing required fields' });
        }
        
        const users = await readUsers();
        
        // Check if user already exists
        if (users.find(user => user.email === email)) {
            return res.status(400).json({ error: 'Email already registered' });
        }
        
        // Hash password
        const hashedPassword = await bcrypt.hash(password, 10);
        
        // Create new user
        const newUser = {
            id: uuidv4(),
            name,
            email,
            password: hashedPassword,
            type,
            company: company || '',
            services: services || '',
            description: description || '',
            createdAt: new Date().toISOString()
        };
        
        users.push(newUser);
        await writeUsers(users);
        
        // Generate JWT token
        const token = jwt.sign(
            { id: newUser.id, email: newUser.email, type: newUser.type },
            JWT_SECRET,
            { expiresIn: '24h' }
        );
        
        // Return user data without password
        const { password: _, ...userWithoutPassword } = newUser;
        
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
        
        const users = await readUsers();
        const user = users.find(u => u.email === email);
        
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
        const users = await readUsers();
        const providers = users
            .filter(user => user.type === 'provider')
            .map(({ password, ...provider }) => provider); // Remove password from response
        
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
        
        const users = await readUsers();
        const searchTerm = q.toLowerCase();
        
        const providers = users
            .filter(user => 
                user.type === 'provider' && 
                (user.services?.toLowerCase().includes(searchTerm) || 
                 user.name.toLowerCase().includes(searchTerm) ||
                 user.description?.toLowerCase().includes(searchTerm))
            )
            .map(({ password, ...provider }) => provider);
        
        res.json(providers);
    } catch (error) {
        console.error('Error searching providers:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Send message (contact provider)
app.post('/api/messages', authenticateToken, async (req, res) => {
    try {
        const { receiverEmail, message } = req.body;
        
        if (!receiverEmail || !message) {
            return res.status(400).json({ error: 'Receiver email and message required' });
        }
        
        const users = await readUsers();
        const receiver = users.find(u => u.email === receiverEmail);
        
        if (!receiver) {
            return res.status(404).json({ error: 'Receiver not found' });
        }
        
        const messages = await readMessages();
        const newMessage = {
            id: uuidv4(),
            senderId: req.user.id,
            senderEmail: req.user.email,
            receiverEmail,
            message,
            createdAt: new Date().toISOString()
        };
        
        messages.push(newMessage);
        await writeMessages(messages);
        
        res.status(201).json({
            message: 'Message sent successfully',
            data: newMessage
        });
        
    } catch (error) {
        console.error('Error sending message:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get platform statistics
app.get('/api/stats', async (req, res) => {
    try {
        const users = await readUsers();
        const messages = await readMessages();
        
        const stats = {
            totalUsers: users.length,
            serviceProviders: users.filter(u => u.type === 'provider').length,
            companies: users.filter(u => u.type === 'company').length,
            totalMessages: messages.length
        };
        
        res.json(stats);
    } catch (error) {
        console.error('Error fetching stats:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Serve frontend files
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../src', 'index.html'));
});

// Initialize database and start server
initializeData().then(() => {
    app.listen(PORT, () => {
        console.log(`🚀 Flowlyne Backend running on http://localhost:${PORT}`);
        console.log(`📊 API endpoints available at http://localhost:${PORT}/api/`);
    });
});
