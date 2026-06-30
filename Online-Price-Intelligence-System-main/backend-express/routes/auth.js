const express = require('express');
const router = express.Router();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const db = require('../config/db');
const { sendResetEmail } = require('../services/email');

// @route   POST /api/auth/register
// ... (existing register code)
router.post('/register', async (req, res) => {
    const { name, email, password } = req.body;

    if (!name || !email || !password) {
        return res.status(400).json({ error: 'Please provide all required fields' });
    }

    try {
        // Check if user already exists
        const userExists = await db.query('SELECT * FROM users WHERE email = $1', [email]);
        if (userExists.rows.length > 0) {
            return res.status(400).json({ error: 'User already exists with this email' });
        }

        // Hash password
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        // Store user in DB
        const query = `
            INSERT INTO users (name, email, password)
            VALUES ($1, $2, $3)
            RETURNING id, name, email;
        `;
        const result = await db.query(query, [name, email, hashedPassword]);
        const user = result.rows[0];

        // Generate JWT
        const token = jwt.sign(
            { id: user.id, email: user.email },
            process.env.JWT_SECRET,
            { expiresIn: '7d' }
        );

        res.status(201).json({
            message: 'User registered successfully',
            token,
            user
        });
    } catch (err) {
        console.error('Error during registration:', err);
        res.status(500).json({ error: 'Internal server error during registration' });
    }
});

// @route   POST /api/auth/login
// ... (existing login code)
router.post('/login', async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        return res.status(400).json({ error: 'Please provide email and password' });
    }

    try {
        // Check if user exists
        const result = await db.query('SELECT * FROM users WHERE email = $1', [email]);
        if (result.rows.length === 0) {
            return res.status(400).json({ error: 'Invalid credentials' });
        }

        const user = result.rows[0];

        // Verify password
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            return res.status(400).json({ error: 'Invalid credentials' });
        }

        // Generate JWT
        const token = jwt.sign(
            { id: user.id, email: user.email },
            process.env.JWT_SECRET,
            { expiresIn: '7d' }
        );

        // Remove password from user object
        delete user.password;

        res.json({
            message: 'Login successful',
            token,
            user
        });
    } catch (err) {
        console.error('Error during login:', err);
        res.status(500).json({ error: 'Internal server error during login' });
    }
});

// @route   POST /api/auth/forgot-password
// @desc    Request password reset token
router.post('/forgot-password', async (req, res) => {
    const { email } = req.body;
    if (!email) return res.status(400).json({ error: 'Intelligence requires an email address.' });

    try {
        const result = await db.query('SELECT * FROM users WHERE email = $1', [email]);
        if (result.rows.length === 0) {
            // Don't reveal user existence for security, but we'll return success to stop timing attacks
            return res.json({ message: 'If that identity exists, a reset link has been dispatched.' });
        }

        const user = result.rows[0];
        const token = crypto.randomBytes(32).toString('hex');
        const expiry = new Date(Date.now() + 3600000); // 1 hour

        await db.query(
            'UPDATE users SET reset_password_token = $1, reset_password_expires = $2 WHERE email = $3',
            [token, expiry, email]
        );

        // Send email — non-fatal: if email service is unconfigured, we log a warning
        // but still return 200 so the route doesn't break in dev environments.
        let emailSent = false;
        try {
            await sendResetEmail(email, token);
            emailSent = true;
            console.log(`✅ Reset email sent successfully to ${email}`);
        } catch (emailErr) {
            console.warn(`⚠️ [forgot-password] Email service failed: ${emailErr.message}`);
            console.warn(`📋 To fix: Add EMAIL_USER and EMAIL_PASS to .env (Gmail App Password)`);
        }

        const resetLink = `http://localhost:5173/reset-password?token=${token}`;
        
        // In development, also return the reset link directly for testing
        const response = {
            message: emailSent 
                ? 'Reset link sent to your email. Check your inbox (and spam folder).' 
                : 'Reset link generated. Email service is not configured. Use the link below for testing:',
            ...(process.env.NODE_ENV === 'development' && { resetLink, token })
        };

        res.json(response);
    } catch (err) {
        console.error('Forgot password error:', err);
        res.status(500).json({ error: 'Neural link failed. Try again later.' });
    }
});

// @route   POST /api/auth/reset-password
// @desc    Reset password using token
router.post('/reset-password', async (req, res) => {
    const { token, password } = req.body;

    if (!token || !password) {
        return res.status(400).json({ error: 'Protocol violated. Token and password required.' });
    }

    try {
        const result = await db.query(
            'SELECT * FROM users WHERE reset_password_token = $1 AND reset_password_expires > NOW()',
            [token]
        );

        if (result.rows.length === 0) {
            return res.status(400).json({ error: 'Token is invalid or has expired.' });
        }

        const user = result.rows[0];
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        await db.query(
            'UPDATE users SET password = $1, reset_password_token = NULL, reset_password_expires = NULL WHERE id = $2',
            [hashedPassword, user.id]
        );

        res.json({ message: 'Neural override successful. New password authorized.' });
    } catch (err) {
        console.error('Reset password error:', err);
        res.status(500).json({ error: 'Decryption failed. Try again later.' });
    }
});

module.exports = router;
