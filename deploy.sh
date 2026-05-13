#!/bin/bash

# Infrastructure Knowledge Graph - Deployment Script
# This script helps deploy the application to production

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Infrastructure Knowledge Graph - Deployment         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Git Push
echo -e "${YELLOW}Step 1: Pushing to GitHub${NC}"
echo "Repository: https://github.com/Khuzaima05/Infra-Knowledge-Graph"
echo ""

read -p "Have you committed all changes? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Pushing to GitHub..."
    git add .
    git commit -m "Production-ready: IBM Cloud Infrastructure Knowledge Graph" || echo "No changes to commit"
    git push origin main
    echo -e "${GREEN}✓ Pushed to GitHub${NC}"
else
    echo "Please commit your changes first:"
    echo "  git add ."
    echo "  git commit -m 'Production-ready: IBM Cloud Infrastructure Knowledge Graph'"
    echo "  git push origin main"
    exit 1
fi

echo ""
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
        echo "Deploying to Railway..."
        echo ""
        echo "Run these commands:"
        echo -e "${BLUE}  cd backend${NC}"
        echo -e "${BLUE}  railway login${NC}"
        echo -e "${BLUE}  railway init${NC}"
        echo -e "${BLUE}  railway add postgresql${NC}"
        echo -e "${BLUE}  railway up${NC}"
        echo ""
        echo "After deployment, get your backend URL:"
        echo -e "${BLUE}  railway status${NC}"
        echo ""
        read -p "Press Enter when backend is deployed..."
        ;;
    2)
        echo ""
        echo "Deploying to Render..."
        echo ""
        echo "1. Go to https://render.com"
        echo "2. Click 'New +' → 'Blueprint'"
        echo "3. Connect your GitHub repository"
        echo "4. Render will auto-deploy using render.yaml"
        echo ""
        read -p "Press Enter when backend is deployed..."
        ;;
    3)
        echo "Skipping backend deployment"
        ;;
esac

echo ""
echo -e "${YELLOW}Step 3: Frontend Deployment to Vercel${NC}"
echo ""

read -p "Enter your backend API URL (e.g., https://your-api.railway.app): " backend_url

if [ -z "$backend_url" ]; then
    echo -e "${RED}Backend URL is required!${NC}"
    exit 1
fi

echo ""
echo "Deploying frontend to Vercel..."
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

# Deploy
echo "Deploying to Vercel..."
vercel --prod

cd ..

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Deployment Complete! 🎉                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo "1. Update backend CORS_ORIGINS with your Vercel URL"
echo "2. Test the application"
echo "3. Monitor logs for any issues"
echo ""
echo "Useful commands:"
echo "  Backend logs (Railway): railway logs"
echo "  Frontend logs: Check Vercel dashboard"
echo ""

# Made with Bob
