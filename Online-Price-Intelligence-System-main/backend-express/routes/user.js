const express = require('express');
const router = express.Router();
const db = require('../config/db');
const auth = require('../middleware/auth');

// @route   GET /api/user/profile
// @desc    Get user profile
router.get('/profile', auth, async (req, res) => {
    try {
        const result = await db.query(
            'SELECT id, name, email, created_at FROM users WHERE id = $1',
            [req.user.id]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'User not found.' });
        }

        res.json(result.rows[0]);
    } catch (err) {
        console.error('Error fetching profile:', err);
        res.status(500).json({ error: 'Internal server error.' });
    }
});

// @route   PUT /api/user/profile
// @desc    Update user profile
router.post('/profile', auth, async (req, res) => {
    const { name, email } = req.body;

    if (!name || !email) {
        return res.status(400).json({ error: 'Name and email are required for update.' });
    }

    try {
        const result = await db.query(
            'UPDATE users SET name = $1, email = $2 WHERE id = $3 RETURNING id, name, email, created_at',
            [name, email, req.user.id]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'User not found.' });
        }

        res.json({
            message: 'Profile updated successfully.',
            user: result.rows[0]
        });
    } catch (err) {
        console.error('Error updating profile:', err);
        if (err.code === '23505') {
            return res.status(400).json({ error: 'Email already in use by another agent.' });
        }
        res.status(500).json({ error: 'Internal server error.' });
    }
});

module.exports = router;
