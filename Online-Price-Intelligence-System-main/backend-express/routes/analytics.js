const express = require('express');
const router = express.Router();
const db = require('../config/db');
const axios = require('axios');
const auth = require('../middleware/auth');

// API: Get Price History (Last 30 days)
router.get('/price-history', async (req, res) => {
    const { productId } = req.query;

    if (!productId) {
        return res.status(400).json({ error: 'productId is required' });
    }

    try {
        const query = `
      SELECT price, recorded_at
      FROM price_history
      WHERE product_id = $1
      AND recorded_at >= NOW() - INTERVAL '30 days'
      ORDER BY recorded_at ASC
    `;
        const result = await db.query(query, [productId]);
        res.json(result.rows);
    } catch (err) {
        console.error('Error fetching price history:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// API: Get Product Recommendations based on Search History
router.get('/recommendations/:userId', auth, async (req, res) => {
    const { userId } = req.params;

    if (parseInt(userId) !== req.user.id) {
        return res.status(401).json({ error: 'Neural link unauthorized. Access denied.' });
    }

    try {
        const historyQuery = `
      SELECT search_query, COUNT(*) as frequency
      FROM search_history
      WHERE user_id = $1
      GROUP BY search_query
      ORDER BY frequency DESC
      LIMIT 1;
    `;
        const historyResult = await db.query(historyQuery, [userId]);

        if (historyResult.rows.length === 0) {
            return res.json([]);
        }

        const topQuery = historyResult.rows[0].search_query;
        const pythonResponse = await axios.get(`http://localhost:8000/api/compare-prices?product=${encodeURIComponent(topQuery)}&limit=6`);

        if (pythonResponse.data && pythonResponse.data.status === 'success') {
            res.json(pythonResponse.data.products);
        } else {
            res.json([]);
        }
    } catch (err) {
        console.error('Error generating recommendations:', err);
        res.json([]);
    }
});

module.exports = router;
