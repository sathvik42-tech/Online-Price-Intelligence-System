const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../.env') });

const { startScheduler } = require('./services/scheduler');

// Routes
const alertRoutes = require('./routes/alerts');
const historyRoutes = require('./routes/history');
const wishlistRoutes = require('./routes/wishlist');
const analyticsRoutes = require('./routes/analytics');
const authRoutes = require('./routes/auth');
const userRoutes = require('./routes/user');

const app = express();
const port = process.env.PORT_EXPRESS || 5001;

// Middleware
app.use(cors());
app.use(express.json());

// Optional gzip compression (won't break if dependency isn't installed yet)
try {
    // eslint-disable-next-line global-require
    const compression = require('compression');
    app.use(compression());
    console.log('Gzip compression enabled');
} catch (e) {
    console.log('Gzip compression not enabled (install `compression` to enable).');
}

// API Routes
app.use('/api/price-alert', alertRoutes);
app.use('/api/search-history', historyRoutes);
app.use('/api/wishlist', wishlistRoutes);
app.use('/api/analytics', analyticsRoutes);
app.use('/api/auth', authRoutes);
app.use('/api/user', userRoutes);

// Health Check
app.get('/health', (req, res) => res.json({ status: 'healthy', timestamp: new Date() }));

// Start Scheduler
startScheduler();

app.listen(port, () => {
    console.log(`Price Intelligence Express server running on port ${port}`);
});
