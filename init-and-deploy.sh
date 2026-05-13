#!/bin/bash

# Infrastructure Knowledge Graph - Complete Setup and Deployment
# This script initializes git and deploys the application

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Infrastructure Knowledge Graph - Setup & Deploy     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 0: Initialize Git Repository
echo -e "${YELLOW}Step 0: Initializing Git Repository${NC}"
echo ""

if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    echo -e "${GREEN}✓ Git repository initialized${NC}"
else
    echo -e "${GREEN}✓ Git repository already exists${NC}"
fi

# Add remote if not exists
if ! git remote | grep -q "origin"; then
    echo "Adding remote repository..."
    git remote add origin https://github.com/Khuzaima05/Infra-Knowledge-Graph.git
    echo -e "${GREEN}✓ Remote added${NC}"
else
    echo -e "${GREEN}✓ Remote already configured${NC}"
fi

echo ""

# Step 1: Commit and Push
echo -e "${YELLOW}Step 1: Committing and Pushing to GitHub${NC}"
echo ""

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/
.pytest_cache/

# Node
node_modules/
.next/
out/
.env.local
.env.production.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
backend/cloned_repos/
backend/*.db
EOF
    echo -e "${GREEN}✓ Created .gitignore${NC}"
fi

# Stage all files
echo "Staging files..."
git add .

# Commit
echo "Committing changes..."
git commit -m "Production-ready: IBM Cloud Infrastructure Knowledge Graph" || echo "No changes to commit"

# Push
echo "Pushing to GitHub..."
git branch -M main
git push -u origin main

echo -e "${GREEN}✓ Pushed to GitHub${NC}"
echo ""

# Step 2: Backend Deployment
echo -e "${YELLOW}Step 2: Backend Deployment${NC}"
echo "Choose your backend deployment platform:"
echo "  1) Railway (Recommended)"
echo "  2) Render"
echo "  3) Skip (deploy manually later)"
echo ""

read -p "Enter choice (1-3): " backend_choice

case $backend_choice in
    1)
        echo ""
        echo "Setting up Railway deployment..."
        echo ""
        
        # Check if railway CLI is installed
        if ! command -v railway &> /dev/null; then
            echo "Installing Railway CLI..."
            npm install -g @railway/cli
        fi
        
        cd backend
        
        echo "Logging into Railway..."
        railway login
        
        echo "Initializing Railway project..."
        railway init
        
        echo "Adding PostgreSQL database..."
        railway add postgresql
        
        echo "Deploying backend..."
        railway up
        
        echo ""
        echo "Getting backend URL..."
        railway status
        
        echo ""
        read -p "Enter your backend URL from above (e.g., https://your-app.railway.app): " backend_url
        
        cd ..
        ;;
    2)
        echo ""
        echo "Deploying to Render..."
        echo ""
        echo "1. Go to https://render.com"
        echo "2. Click 'New +' → 'Blueprint'"
        echo "3. Connect repository: Khuzaima05/Infra-Knowledge-Graph"
        echo "4. Render will auto-deploy using render.yaml"
        echo ""
        read -p "Enter your backend URL after deployment: " backend_url
        ;;
    3)
        echo "Skipping backend deployment"
        read -p "Enter your backend URL (or press Enter to skip frontend deployment): " backend_url
        ;;
esac

if [ -z "$backend_url" ]; then
    echo ""
    echo -e "${YELLOW}Backend URL not provided. Skipping frontend deployment.${NC}"
    echo "You can deploy frontend later using: cd frontend && vercel --prod"
    exit 0
fi

echo ""

# Step 3: Frontend Deployment
echo -e "${YELLOW}Step 3: Frontend Deployment to Vercel${NC}"
echo ""

cd frontend

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Installing Vercel CLI..."
    npm install -g vercel
fi

# Set environment variable
echo "Setting environment variable..."
echo "NEXT_PUBLIC_API_URL=$backend_url" > .env.production

# Login to Vercel
echo "Logging into Vercel..."
vercel login

# Deploy
echo "Deploying to Vercel..."
vercel --prod

cd ..

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Deployment Complete! 🎉                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Your application is now live!"
echo ""
echo "Next steps:"
echo "1. Copy your Vercel URL from the output above"
echo "2. Update backend CORS_ORIGINS:"
if [ "$backend_choice" = "1" ]; then
    echo "   cd backend && railway variables set CORS_ORIGINS=https://your-app.vercel.app"
elif [ "$backend_choice" = "2" ]; then
    echo "   Update CORS_ORIGINS in Render dashboard"
fi
echo "3. Test your application"
echo "4. Try analyzing: https://github.com/terraform-ibm-modules/terraform-ibm-landing-zone-vpc"
echo ""
echo "Useful URLs:"
echo "  GitHub: https://github.com/Khuzaima05/Infra-Knowledge-Graph"
echo "  Backend: $backend_url"
echo "  API Docs: $backend_url/docs"
echo "  Health Check: $backend_url/health"
echo ""

# Made with Bob
