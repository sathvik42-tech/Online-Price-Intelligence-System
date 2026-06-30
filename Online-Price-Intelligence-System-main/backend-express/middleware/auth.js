const jwt = require('jsonwebtoken');

const auth = (req, res, next) => {
    // Get token from header
    const authHeader = req.header('Authorization');

    if (!authHeader) {
        return res.status(401).json({ error: 'No intelligence token, authorization denied.' });
    }

    try {
        const token = authHeader.replace('Bearer ', '');
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded;
        next();
    } catch (err) {
        res.status(401).json({ error: 'Token is not valid.' });
    }
};

module.exports = auth;
