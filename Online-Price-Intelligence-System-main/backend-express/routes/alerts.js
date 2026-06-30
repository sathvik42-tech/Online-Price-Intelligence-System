const express = require('express');
const router = express.Router();
const db = require('../config/db');
const auth = require('../middleware/auth');

// API: Set Price Alert
router.post('/', auth, async (req, res) => {
    const { product_id, product_name, current_price, target_price } = req.body;
    const user_id = req.user.id;

    if (!product_id || !product_name || !target_price) {
        return res.status(400).json({ error: 'Missing required fields: product_id, product_name, target_price' });
    }

    try {
        const query = `
            INSERT INTO price_alerts (user_id, product_id, product_name, current_price, target_price)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *;
        `;
        const values = [user_id, product_id, product_name, current_price, target_price];
        const result = await db.query(query, values);
        res.status(201).json({ message: 'Price alert created successfully', alert: result.rows[0] });
    } catch (err) {
        console.error('Error setting price alert:', err);
        res.status(500).json({ error: 'Failed to create price alert' });
    }
});

// API: Get Price Alerts for User
router.get('/user/:userId', auth, async (req, res) => {
    const { userId } = req.params;
    const userId_num = parseInt(userId);
    const page = Math.max(parseInt(req.query.page || '1', 10) || 1, 1);
    const perPageRaw = parseInt(req.query.per_page || '20', 10) || 20;
    const perPage = Math.min(Math.max(perPageRaw, 1), 50);
    const offset = (page - 1) * perPage;

    // Security check: Only allow users to access their own alerts
    if (userId_num !== req.user.id) {
        return res.status(401).json({ error: 'Unauthorized: You can only access your own price alerts' });
    }

    try {
        const countRes = await db.query(
            'SELECT COUNT(*)::int AS total FROM price_alerts WHERE user_id = $1',
            [userId_num]
        );
        const total = countRes.rows?.[0]?.total || 0;

        const query = `
            SELECT id, user_id, product_id, product_name, current_price, target_price, created_at
            FROM price_alerts
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        `;
        const result = await db.query(query, [userId_num, perPage, offset]);
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
        console.error('Error fetching user price alerts:', err);
        res.status(500).json({ error: 'Failed to retrieve price alerts' });
    }
});

// API: Delete Price Alert
router.delete('/:alertId', auth, async (req, res) => {
    const { alertId } = req.params;

    try {
        // Check ownership first
        const check = await db.query('SELECT user_id FROM price_alerts WHERE id = $1', [alertId]);
        if (check.rows.length === 0) {
            return res.status(404).json({ error: 'Price alert not found' });
        }

        if (check.rows[0].user_id !== req.user.id) {
            return res.status(401).json({ error: 'Unauthorized: You can only delete your own alerts' });
        }

        await db.query('DELETE FROM price_alerts WHERE id = $1', [alertId]);
        res.json({ message: 'Price alert deleted successfully' });
    } catch (err) {
        console.error('Error deleting price alert:', err);
        res.status(500).json({ error: 'Failed to delete price alert' });
    }
});

// API: Update Price Alert
router.put('/:alertId', auth, async (req, res) => {
    const { alertId } = req.params;
    const { target_price } = req.body;

    if (!target_price) {
        return res.status(400).json({ error: 'target_price is required' });
    }

    try {
        // Check ownership first
        const check = await db.query('SELECT user_id FROM price_alerts WHERE id = $1', [alertId]);
        if (check.rows.length === 0) {
            return res.status(404).json({ error: 'Price alert not found' });
        }

        if (check.rows[0].user_id !== req.user.id) {
            return res.status(401).json({ error: 'Unauthorized: You can only update your own alerts' });
        }

        const query = 'UPDATE price_alerts SET target_price = $1 WHERE id = $2 RETURNING *';
        const result = await db.query(query, [target_price, alertId]);
        res.json({ message: 'Price alert updated successfully', alert: result.rows[0] });
    } catch (err) {
        console.error('Error updating price alert:', err);
        res.status(500).json({ error: 'Failed to update price alert' });
    }
});

module.exports = router;

