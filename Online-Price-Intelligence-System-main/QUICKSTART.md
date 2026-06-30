# Quick Start Guide - Authentication Integrated System

## Prerequisites

- Node.js 16+ and npm
- PostgreSQL 12+
- Python 3.8+ (for ML backend)

## 1️⃣ Setup Database

```bash
# Create database
createdb price_intelligence_db

# Run schema
psql -U postgres -d price_intelligence_db < backend-express/db/schema.sql

# Run migration (converts price_alerts to use user_id)
cd backend-express
node db/migrate.js
```

## 2️⃣ Configure Environment

**Backend** (`backend-express/.env`):
```bash
cp backend-express/.env.example backend-express/.env
```

Edit `.env` with your database credentials:
```env
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
JWT_SECRET=your_secret_key_here
```

**Frontend** (`frontend/.env` - optional):
```bash
cp frontend/.env.example frontend/.env
# No changes needed for development (Vite proxy handles forwarding)
```

## 3️⃣ Start Services

**Terminal 1 - Backend:**
```bash
cd backend-express
npm install
npm start
```
✓ Listens on http://localhost:5001

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```
✓ Opens http://localhost:5173

**Terminal 3 - Python Backend (optional):**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

## 4️⃣ Test Authentication

### Register New User
1. Open http://localhost:5173/login
2. Click "Sign Up"
3. Fill form and click "Register"
4. ✓ Redirected to dashboard

### Test Features
- **Dashboard**: Should show welcome with your name
- **Wishlist**: Add/remove products
- **Results**: Set price alerts and add to wishlist
- **Profile**: Edit your information
- **History**: Your searches are saved

### Logout
- Click avatar → "Logout"
- ✓ Redirected to login page

## 5️⃣ Verify Integration

Run the verification script:
```bash
bash verify_auth_integration.sh
```

## 📊 How It Works

1. **Register/Login** - Get JWT token stored in localStorage
2. **API Calls** - Token automatically sent in Authorization header
3. **Protected Routes** - Backend validates token, checks user ownership
4. **Session** - Token expires after 7 days
5. **Logout** - Token removed from storage

```
User → Frontend → api.js (adds token) → Backend → auth middleware → Route handler
```

## 🎯 Key Features

✅ **Wishlist** - Personal per-user collection
✅ **Price Alerts** - Track products tied to your account
✅ **Search History** - Your search queries are saved
✅ **Dashboard** - Overview of your watchlist and alerts
✅ **Profile** - Manage your account settings
✅ **Password Reset** - Recover your account via email

## ⚙️ API Endpoints

### Authentication (Public)
- `POST /api/auth/register` - Register
- `POST /api/auth/login` - Login
- `POST /api/auth/forgot-password` - Reset request
- `POST /api/auth/reset-password` - Reset with token

### Protected (Require Token)
- `GET /api/wishlist/:userId` - Your wishlist
- `POST /api/wishlist` - Add item
- `DELETE /api/wishlist/:id` - Remove item
- `GET /api/price-alert/user/:userId` - Your alerts
- `POST /api/price-alert` - Create alert
- `DELETE /api/price-alert/:alertId` - Delete alert
- `GET /api/search-history/:userId` - Your searches
- `POST /api/search-history` - Record search
- `GET /api/user/profile` - Your profile
- `POST /api/user/profile` - Update profile

## 🐛 Common Issues

### _Cannot find localhost:5001_
- Backend not running? Start with: `cd backend-express && npm start`
- Check port: `lsof -i :5001`

### _401 Unauthorized_
- Login first to get token
- Token in localStorage? Check: `localStorage.getItem('intelToken')`

### _Database connection failed_
- PostgreSQL running? `psql -U postgres -c "SELECT 1;"`
- Check .env credentials
- Database exists? `psql -l | grep price_intelligence`

### _Cannot view other users' data_
- Each user sees only their own data
- Trying to access `/api/wishlist/5` as user 3?
- Backend checks: `if (userId !== req.user.id) return 401`

## 📚 Learn More

- **Full Guide**: See [AUTHENTICATION.md](AUTHENTICATION.md)
- **API Details**: See [AUTH_INTEGRATION_SUMMARY.md](AUTH_INTEGRATION_SUMMARY.md)
- **Troubleshooting**: See AUTHENTICATION.md → Troubleshooting section

## 🚀 Production Deployment

Before going live:

1. Change JWT_SECRET to random 32+ char string
2. Set NODE_ENV=production
3. Use HTTPS/SSL certificates
4. Set up email service for password resets
5. Configure CORS for your domain
6. Use environment variables (no hardcoded secrets)
7. Enable database backups
8. Set up monitoring and logging

## 📞 Quick Support

**Check logs:**
```bash
# Backend errors
npm start  # in backend-express

# Frontend errors
Browser → DevTools → Console

# Database
psql -U postgres -d price_intelligence_db
# SELECT * FROM users;
# SELECT * FROM price_alerts;
```

## ✨ What's Next?

- [ ] Test all user flows
- [ ] Configure email service (optional)
- [ ] Set up password reset emails
- [ ] Customize branding
- [ ] Configure production database
- [ ] Set up CI/CD pipeline
- [ ] Enable monitoring and alerts

---

**Status**: ✅ Ready to run
**Test Time**: ~5 minutes to verify auth works
**Need Help**: See AUTHENTICATION.md
