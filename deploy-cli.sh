#!/bin/bash

# CLI Deployment Script for Infrastructure Knowledge Graph
# This script deploys both frontend (Vercel) and backend (Render) using CLI tools

set -e  # Exit on error

echo "🚀 Infrastructure Knowledge Graph - CLI Deployment"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Push to GitHub
echo -e "${BLUE}Step 1: Pushing to GitHub...${NC}"
echo "=================================================="

if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: Infrastructure Knowledge Graph"
    git branch -M main
    git remote add origin https://github.com/Khuzaima05/Infra-Knowledge-Graph.git
fi

echo "Pushing to GitHub..."
git add .
git commit -m "Deploy: Infrastructure Knowledge Graph" || echo "No changes to commit"
git push origin main

echo -e "${GREEN}✓ Code pushed to GitHub${NC}"
echo ""

# Step 2: Deploy Frontend to Vercel
echo -e "${BLUE}Step 2: Deploying Frontend to Vercel...${NC}"
echo "=================================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Installing Vercel CLI..."
    npm install -g vercel
fi

cd frontend

echo "Deploying to Vercel..."
echo "Note: You may need to login if this is your first time"
vercel --prod

cd ..

echo -e "${GREEN}✓ Frontend deployed to Vercel${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Copy your Vercel URL from the output above${NC}"
echo ""

# Step 3: Deploy Backend to Render
echo -e "${BLUE}Step 3: Deploying Backend to Render...${NC}"
echo "=================================================="

# Check if Render CLI is installed
if ! command -v render &> /dev/null; then
    echo "Render CLI not found. Installing..."
    
    # Try Homebrew first (macOS)
    if command -v brew &> /dev/null; then
        echo "Installing via Homebrew..."
        brew tap render-oss/render 2>/dev/null || true
        brew install render 2>/dev/null || true
    fi
    
    # Try npm if brew failed or not available
    if ! command -v render &> /dev/null; then
        echo "Installing via npm..."
        npm install -g @render/cli
    fi
fi

# Check if render.yaml exists
if [ ! -f render.yaml ]; then
    echo -e "${RED}Error: render.yaml not found${NC}"
    echo "Please ensure render.yaml exists in the project root"
    exit 1
fi

echo "Deploying to Render..."
echo "Note: You may need to login if this is your first time"

# Try to deploy with Render CLI
if command -v render &> /dev/null; then
    render deploy
    echo -e "${GREEN}✓ Backend deployed to Render${NC}"
else
    echo -e "${YELLOW}⚠️  Render CLI installation failed${NC}"
    echo ""
    echo "Please deploy backend manually via Render Dashboard:"
    echo "1. Go to https://render.com/dashboard"
    echo "2. Click 'New +' → 'Blueprint'"
    echo "3. Connect your GitHub repo: Khuzaima05/Infra-Knowledge-Graph"
    echo "4. Render will auto-detect render.yaml and deploy"
    echo ""
fi

echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Copy your Render backend URL from the output above${NC}"
echo ""

# Step 4: Configuration Instructions
echo -e "${BLUE}Step 4: Connect Frontend and Backend${NC}"
echo "=================================================="
echo ""
echo "Run these commands to connect your frontend to backend:"
echo ""
echo -e "${YELLOW}cd frontend${NC}"
echo -e "${YELLOW}vercel env add NEXT_PUBLIC_API_URL production${NC}"
echo "  → Enter your Render backend URL (e.g., https://infra-knowledge-graph-api.onrender.com)"
echo ""
echo -e "${YELLOW}vercel --prod${NC}"
echo "  → Redeploy frontend with new environment variable"
echo ""
echo "Then update backend CORS via Render Dashboard:"
echo "1. Go to your service on Render"
echo "2. Environment → Add: CORS_ORIGINS"
echo "3. Value: https://your-frontend.vercel.app,http://localhost:3000"
echo ""

# Step 5: Verification
echo -e "${BLUE}Step 5: Verify Deployment${NC}"
echo "=================================================="
echo ""
echo "Test your backend:"
echo "  curl https://your-backend.onrender.com/health"
echo ""
echo "Test your frontend:"
echo "  Open https://your-frontend.vercel.app in browser"
echo ""

# Summary
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "=================================================="
echo ""
echo "What was deployed:"
echo "  ✓ Code pushed to GitHub"
echo "  ✓ Frontend deployed to Vercel"
echo "  ✓ Backend deployed to Render (or instructions provided)"
echo ""
echo "Next steps:"
echo "  1. Copy your Vercel frontend URL"
echo "  2. Copy your Render backend URL"
echo "  3. Connect them using the commands above"
echo "  4. Test your deployment"
echo ""
echo "Need help? Check:"
echo "  - CLI_DEPLOYMENT.md for detailed instructions"
echo "  - VERCEL_DEPLOYMENT.md for alternative methods"
echo ""
echo "Happy deploying! 🎉"

# Made with Bob
