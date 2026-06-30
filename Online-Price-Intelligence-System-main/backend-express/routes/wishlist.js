const express = require('express');
const router = express.Router();
const db = require('../config/db');
const auth = require('../middleware/auth');

// API: Add to Wishlist
router.post('/', auth, async (req, res) => {
    const { product_id, product_name, product_image, price, store, product_link } = req.body;
    const user_id = req.user.id;

    try {
        const query = `
      INSERT INTO wishlist (user_id, product_id, product_name, product_image, price, store, product_link)
      VALUES ($1, $2, $3, $4, $5, $6, $7)
      RETURNING id, user_id, product_id, product_name, product_image, price, store, product_link, created_at;
    `;
        const values = [user_id, product_id, product_name, product_image, price, store, product_link];
        const result = await db.query(query, values);
        res.status(201).json({ message: 'Product archived in neural wishlist.', item: result.rows[0] });
    } catch (err) {
        console.error('Error adding to wishlist:', err);
        res.status(500).json({ error: 'Failed to archive intel item.' });
    }
});

// API: Get Wishlist
router.get('/:userId', auth, async (req, res) => {
    const { userId } = req.params;
    const page = Math.max(parseInt(req.query.page || '1', 10) || 1, 1);
    const perPageRaw = parseInt(req.query.per_page || '20', 10) || 20;
    const perPage = Math.min(Math.max(perPageRaw, 1), 50);
    const offset = (page - 1) * perPage;

    if (parseInt(userId) !== req.user.id) {
        return res.status(401).json({ error: 'Authorization failure. Resource lock engaged.' });
    }

    try {
        const countRes = await db.query(
            'SELECT COUNT(*)::int AS total FROM wishlist WHERE user_id = $1',
            [userId]
        );
        const total = countRes.rows?.[0]?.total || 0;

        const query = `
            SELECT
                id, user_id, product_id, product_name, product_image,
                price, store, product_link, created_at
            FROM wishlist
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
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
        console.error('Error fetching wishlist:', err);
        res.status(500).json({ error: 'Neural link failed to retrieve records.' });
    }
});

// API: Remove from Wishlist
router.delete('/:id', auth, async (req, res) => {
    const { id } = req.params;

    try {
        // Ownership check
        const check = await db.query('SELECT user_id FROM wishlist WHERE id = $1', [id]);
        if (check.rows.length === 0) return res.status(404).json({ error: 'Intel record not found.' });
        if (check.rows[0].user_id !== req.user.id) return res.status(401).json({ error: 'Encryption mismatch. Deletion unauthorized.' });

        await db.query('DELETE FROM wishlist WHERE id = $1', [id]);
        res.json({ message: 'Intel record purged from archive.' });
    } catch (err) {
        console.error('Error removing from wishlist:', err);
        res.status(500).json({ error: 'Internal memory error during purge.' });
    }
});

module.exports = router;
