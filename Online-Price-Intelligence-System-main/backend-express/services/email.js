const nodemailer = require('nodemailer');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../../.env') });

const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS,
    },
});

async function sendAlertEmail(userEmail, product) {
    const mailOptions = {
        from: process.env.EMAIL_USER,
        to: userEmail,
        subject: `🔥 Price Drop Alert: ${product.product_name}`,
        html: `
            <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #ddd;">
                <h2 style="color: #4f46e5;">Price Alert Triggered!</h2>
                <p>Good news! The product you were watching has dropped in price.</p>
                <div style="background: #f9fafb; padding: 15px; border-radius: 8px;">
                    <h3>${product.product_name}</h3>
                    <p><strong>Current Price:</strong> ₹${product.current_price}</p>
                    <p><strong>Target Price:</strong> ₹${product.target_price}</p>
                </div>
                <p style="margin-top: 20px;">
                    <a href="${product.product_link}" style="background: #4f46e5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Deal</a>
                </p>
            </div>
        `
    };

    return transporter.sendMail(mailOptions);
}

async function sendResetEmail(userEmail, token) {
    const resetLink = `http://localhost:5173/reset-password?token=${token}`;
    const mailOptions = {
        from: process.env.EMAIL_USER,
        to: userEmail,
        subject: `🔑 Intelligence Reset: Password Authorization Required`,
        html: `
            <div style="font-family: 'Segoe UI', Arial, sans-serif; padding: 40px; background: #050810; color: #ffffff; border-radius: 20px;">
                <h2 style="color: #6366f1; text-transform: uppercase; letter-spacing: 2px;">Neural Overwrite Request</h2>
                <p style="color: #94a3b8;">A protocol for password reset has been initiated for your intelligence profile.</p>
                <div style="margin: 30px 0; padding: 20px; border-left: 4px solid #6366f1; background: rgba(99, 102, 241, 0.1);">
                    <p style="margin: 0; font-weight: bold; color: #e2e8f0;">Security Token Issued</p>
                    <p style="margin: 5px 0 0 0; font-size: 12px; color: #64748b;">Expires in 60 minutes</p>
                </div>
                <p style="margin-top: 30px;">
                    <a href="${resetLink}" style="background: #6366f1; color: white; padding: 14px 28px; text-decoration: none; border-radius: 12px; font-weight: bold; display: inline-block;">Authorize Reset</a>
                </p>
                <p style="margin-top: 40px; font-size: 11px; color: #475569;">If you did not initiate this override, please ignore this transmission. Your current encryption remains secure.</p>
            </div>
        `
    };

    return transporter.sendMail(mailOptions);
}

module.exports = { sendAlertEmail, sendResetEmail };
