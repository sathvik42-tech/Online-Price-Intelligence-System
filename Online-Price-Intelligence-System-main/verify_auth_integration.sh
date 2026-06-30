#!/bin/bash

# Authentication Integration Verification Checklist
# This script verifies that authentication has been properly integrated

echo "==================================="
echo "Auth Integration Verification"
echo "==================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_mark="${GREEN}✓${NC}"
cross_mark="${RED}✗${NC}"

# Counter
total_checks=0
passed_checks=0

# Function to check if file exists and contains text
check_file_contains() {
    local file=$1
    local text=$2
    local description=$3
    
    total_checks=$((total_checks + 1))
    
    if grep -q "$text" "$file" 2>/dev/null; then
        echo -e "${check_mark} $description"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "${cross_mark} $description"
        echo "        File: $file"
        echo "        Missing: $text"
    fi
}

# Function to check if file exists
check_file_exists() {
    local file=$1
    local description=$2
    
    total_checks=$((total_checks + 1))
    
    if [ -f "$file" ]; then
        echo -e "${check_mark} $description"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "${cross_mark} $description"
        echo "        Missing: $file"
    fi
}

echo "📦 BACKEND FILES"
echo "----------------------------------------"
check_file_exists "backend-express/middleware/auth.js" "Auth middleware exists"
check_file_exists "backend-express/routes/auth.js" "Auth routes exist"
check_file_exists "backend-express/routes/alerts.js" "Alerts routes exist"
check_file_exists "backend-express/routes/wishlist.js" "Wishlist routes exist"
check_file_exists "backend-express/routes/history.js" "History routes exist"
check_file_exists "backend-express/routes/user.js" "User routes exist"
check_file_exists "backend-express/db/schema.sql" "Database schema exists"
check_file_exists "backend-express/db/migrate.js" "Migration script exists"
check_file_exists "backend-express/.env.example" "Backend .env.example exists"

echo ""
echo "🎨 FRONTEND FILES"
echo "----------------------------------------"
check_file_exists "frontend/src/api.js" "API client exists"
check_file_exists "frontend/src/pages/AuthPage.jsx" "Auth page exists"
check_file_exists "frontend/src/pages/DashboardPage.jsx" "Dashboard page exists"
check_file_exists "frontend/src/pages/WishlistPage.jsx" "Wishlist page exists"
check_file_exists "frontend/src/pages/ProfilePage.jsx" "Profile page exists"
check_file_exists "frontend/.env.example" "Frontend .env.example exists"

echo ""
echo "📚 DOCUMENTATION"
echo "----------------------------------------"
check_file_exists "AUTHENTICATION.md" "Authentication guide exists"
check_file_exists "AUTH_INTEGRATION_SUMMARY.md" "Integration summary exists"

echo ""
echo "🔐 AUTHENTICATION IMPLEMENTATION"
echo "----------------------------------------"
check_file_contains "backend-express/middleware/auth.js" "jwt.verify" "JWT verification implemented"
check_file_contains "backend-express/routes/auth.js" "bcrypt.hash" "Password hashing implemented"
check_file_contains "backend-express/routes/auth.js" "jwt.sign" "JWT token generation implemented"
check_file_contains "frontend/src/api.js" "Authorization" "Bearer token in header"
check_file_contains "frontend/src/api.js" "401" "401 redirect handling"
check_file_contains "frontend/src/pages/AuthPage.jsx" "localStorage.setItem.*intelToken" "Token storage"

echo ""
echo "🔗 API INTEGRATION"
echo "----------------------------------------"
check_file_contains "frontend/src/pages/DashboardPage.jsx" "import.*apiGet.*api" "Dashboard uses api.js"
check_file_contains "frontend/src/pages/WishlistPage.jsx" "import.*api" "Wishlist uses api.js"
check_file_contains "frontend/src/pages/ProfilePage.jsx" "import.*apiGet.*apiPost.*api" "Profile uses api.js"
check_file_contains "frontend/src/pages/ResultsPage.jsx" "import.*apiPost.*api" "Results uses api.js"
check_file_contains "backend-express/routes/alerts.js" "user_id" "Alerts use user_id"

echo ""
echo "📋 DATABASE SCHEMA"
echo "----------------------------------------"
check_file_contains "backend-express/db/schema.sql" "FOREIGN KEY (user_id)" "Foreign key constraints"
check_file_contains "backend-express/db/schema.sql" "ON DELETE CASCADE" "Cascading deletes"
check_file_contains "backend-express/db/schema.sql" "NOT NULL" "NOT NULL constraints"
check_file_contains "backend-express/db/schema.sql" "CREATE INDEX" "Database indexes"

echo ""
echo "🛡️ SECURITY FEATURES"
echo "----------------------------------------"
check_file_contains "backend-express/routes/alerts.js" "if (parseInt(userId) !== req.user.id)" "User isolation in alerts"
check_file_contains "backend-express/routes/wishlist.js" "if (parseInt(userId) !== req.user.id)" "User isolation in wishlist"
check_file_contains "backend-express/routes/history.js" "if (parseInt(userId) !== req.user.id)" "User isolation in history"
check_file_contains "frontend/src/api.js" "handleUnauthorised()" "Logout on auth failure"

echo ""
echo "==================================="
echo "SUMMARY"
echo "==================================="
echo "Checks Passed: $passed_checks / $total_checks"
echo ""

if [ $passed_checks -eq $total_checks ]; then
    echo -e "${GREEN}✓ All checks passed! Authentication integration is complete.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Copy .env.example to .env in both backend-express and frontend"
    echo "2. Fill in your database credentials in backend-express/.env"
    echo "3. Run: node backend-express/db/migrate.js"
    echo "4. Start the servers:"
    echo "   - Backend: cd backend-express && npm install && npm start"
    echo "   - Frontend: cd frontend && npm install && npm run dev"
    echo "5. Test the auth flow: Register → Login → Test features"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please review the issues above.${NC}"
    echo ""
    echo "Failed checks:"
    grep "${cross_mark}" <<< "$output" | head -5
    exit 1
fi
