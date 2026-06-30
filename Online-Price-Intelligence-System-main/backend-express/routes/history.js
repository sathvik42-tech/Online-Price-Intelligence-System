const express = require('express');
const router = express.Router();
const db = require('../config/db');
const auth = require('../middleware/auth');

// API: Record Search History
router.post('/', auth, async (req, res) => {
    const { search_query } = req.body;
    const user_id = req.user.id;

    try {
        const query = `
      INSERT INTO search_history (user_id, search_query)
      VALUES ($1, $2)
      RETURNING *;
    `;
        const result = await db.query(query, [user_id, search_query]);
        res.status(201).json({ message: 'Neural scan recorded.', entry: result.rows[0] });
    } catch (err) {
        console.error('Error recording search history:', err);
        res.status(500).json({ error: 'Transmission failure in search records.' });
    }
});

// API: Get Search History (Last 20)
router.get('/:userId', auth, async (req, res) => {
    const { userId } = req.params;
    const page = Math.max(parseInt(req.query.page || '1', 10) || 1, 1);
    const perPageRaw = parseInt(req.query.per_page || '20', 10) || 20;
    const perPage = Math.min(Math.max(perPageRaw, 1), 50);
    const offset = (page - 1) * perPage;

    // Security check: Only allow users to access their own history
    if (parseInt(userId) !== req.user.id) {
        return res.status(401).json({ error: 'Access denied. Identity mismatch detected.' });
    }

    try {
        const countRes = await db.query(
            'SELECT COUNT(*)::int AS total FROM search_history WHERE user_id = $1',
            [userId]
        );
        const total = countRes.rows?.[0]?.total || 0;

        const query = `
            SELECT id, user_id, search_query, search_time
            FROM search_history
            WHERE user_id = $1
            ORDER BY search_time DESC
            LIMIT $2 OFFSET $3;
        `;
        const result = await db.query(query, [userId, perPage, offset]);

        res.json({
            items: result.rows,
            pagination: {
                page,
                per_page: perPage,
                total,
                has_more: offset + result.rows.length < total,
            },
        });
    } catch (err) {
        console.error('Error fetching search history:', err);
        res.status(500).json({ error: 'Failed to retrieve neural memories.' });
    }
});

module.exports = router;
