const cron = require('node-cron');
const axios = require('axios');
const db = require('../config/db');
const { sendAlertEmail } = require('./email');

async function checkPrices() {
    console.log('Running scheduled price check...');
    try {
        const alerts = await db.query('SELECT * FROM price_alerts');

        for (const alert of alerts.rows) {
            try {
                const pythonApiUrl = `http://localhost:8000/api/compare-prices?product=${encodeURIComponent(alert.product_name)}`;
                const response = await axios.get(pythonApiUrl);

                if (response.data && response.data.status === 'success') {
                    const products = response.data.products;
                    const lowestPrice = Math.min(...products.map(p => parseFloat(p.price)).filter(price => price > 0));

                    console.log(`Checking ${alert.product_name}: Lowest = ₹${lowestPrice}, Target = ₹${alert.target_price}`);

                    if (lowestPrice <= alert.target_price) {
                        await sendAlertEmail(alert, lowestPrice);
                        await db.query('DELETE FROM price_alerts WHERE id = $1', [alert.id]);
                        console.log(`Alert triggered and removed for ${alert.user_email}`);
                    }
                }
            } catch (innerErr) {
                console.error(`Error checking price for alert ${alert.id}:`, innerErr.message);
            }
        }
    } catch (err) {
        console.error('Error fetching alerts:', err);
    }
}

// Background Scheduler: Run every hour
const startScheduler = () => {
    cron.schedule('0 * * * *', checkPrices);
    console.log('Price Check Scheduler Started (Hourly)');
};

module.exports = { startScheduler };
