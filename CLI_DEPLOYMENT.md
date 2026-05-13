# CLI Deployment Guide - Step by Step

Follow these commands exactly to deploy your application using CLI tools.

---

## Prerequisites

First, push your code to GitHub:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Infrastructure Knowledge Graph"

# Add remote
git remote add origin https://github.com/Khuzaima05/Infra-Knowledge-Graph.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Part 1: Deploy Frontend (Vercel CLI)

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Login to Vercel

```bash
vercel login
```

This will:
- Open your browser
- Ask you to login/signup
- Confirm authentication

### Step 3: Navigate to Frontend

```bash
cd frontend
```

### Step 4: Deploy to Production

```bash
vercel --prod
```

**What happens:**
1. Vercel asks: "Set up and deploy?" → Press **Y**
2. "Which scope?" → Choose your account
3. "Link to existing project?" → Press **N** (first time)
4. "What's your project's name?" → Press **Enter** (uses default)
5. "In which directory is your code located?" → Press **Enter** (current dir)
6. Vercel detects Next.js automatically
7. "Want to override settings?" → Press **N**
8. Deployment starts!

**Output:**
```
✓ Production: https://infra-knowledge-graph-abc123.vercel.app [2m]
```

**Save this URL!** You'll need it for the backend CORS configuration.

### Step 5: Set Environment Variable

```bash
# Set the backend URL (we'll get this after deploying backend)
vercel env add NEXT_PUBLIC_API_URL production
# When prompted, enter: https://your-backend-url.onrender.com
```

---

## Part 2: Deploy Backend (Render CLI)

### Step 1: Install Render CLI

```bash
# Install via Homebrew (macOS)
brew tap render-oss/render
brew install render

# OR via npm
npm install -g @render/cli
```

### Step 2: Login to Render

```bash
render login
```

This will:
- Open your browser
- Ask you to login/signup
- Generate API key
- Save credentials

### Step 3: Create render.yaml

I'll create this file for you:

```bash
cd ..  # Go back to project root
```

### Step 4: Deploy Backend

```bash
render deploy
```

**What happens:**
1. Render reads `render.yaml`
2. Creates web service for backend
3. Creates PostgreSQL database
4. Links them together
5. Deploys!

**Output:**
```
✓ Service created: infra-knowledge-graph-api
✓ Database created: infra-knowledge-graph-db
✓ Deploying...
✓ Live at: https://infra-knowledge-graph-api.onrender.com
```

**Save this URL!** This is your backend API URL.

---

## Part 3: Connect Frontend and Backend

### Step 1: Update Frontend Environment Variable

```bash
cd frontend

# Update the API URL with your actual Render backend URL
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://infra-knowledge-graph-api.onrender.com

# Redeploy frontend to use new env var
vercel --prod
```

### Step 2: Update Backend CORS

```bash
# Add CORS origin via Render dashboard or CLI
render env set CORS_ORIGINS="https://your-frontend.vercel.app,http://localhost:3000"
```

---

## Part 4: Verify Deployment

### Test Backend

```bash
# Health check
curl https://infra-knowledge-graph-api.onrender.com/health

# API docs
open https://infra-knowledge-graph-api.onrender.com/docs
```

### Test Frontend

```bash
# Open in browser
open https://your-frontend.vercel.app
```

---

## Complete CLI Commands (Copy-Paste)

Here's everything in one script:

```bash
#!/bin/bash

echo "🚀 Starting deployment..."

# 1. Push to GitHub
echo "📦 Pushing to GitHub..."
git add .
git commit -m "Deploy: Infrastructure Knowledge Graph"
git push origin main

# 2. Deploy Frontend
echo "🎨 Deploying frontend to Vercel..."
cd frontend
npm install -g vercel
vercel login
vercel --prod
cd ..

# 3. Deploy Backend
echo "⚙️ Deploying backend to Render..."
brew install render  # or: npm install -g @render/cli
render login
render deploy

# 4. Get URLs
echo "✅ Deployment complete!"
echo ""
echo "Frontend: Check Vercel output above"
echo "Backend: Check Render output above"
echo ""
echo "Next steps:"
echo "1. Copy your backend URL from Render output"
echo "2. Run: cd frontend && vercel env add NEXT_PUBLIC_API_URL production"
echo "3. Enter your backend URL when prompted"
echo "4. Run: vercel --prod"
```

---

## Alternative: Render Dashboard (Easier for Backend)

If Render CLI doesn't work, use the dashboard:

1. Go to https://render.com/dashboard
2. Click **New +** → **Web Service**
3. Connect GitHub: `Khuzaima05/Infra-Knowledge-Graph`
4. Configure:
   - **Name:** `infra-knowledge-graph-api`
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Click **Create Web Service**
6. Add PostgreSQL:
   - **New +** → **PostgreSQL**
   - Link to your web service

---

## Troubleshooting

### Vercel CLI Issues

```bash
# Clear cache
vercel logout
vercel login

# Force reinstall
npm uninstall -g vercel
npm install -g vercel
```

### Render CLI Issues

```bash
# Check installation
render --version

# Reinstall
brew uninstall render
brew install render

# Or use npm version
npm install -g @render/cli
```

### Can't find commands

```bash
# Add to PATH (macOS/Linux)
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.zshrc
source ~/.zshrc
```

---

## Quick Reference

### Vercel Commands

```bash
vercel login              # Login
vercel                    # Deploy preview
vercel --prod             # Deploy production
vercel env ls             # List env vars
vercel env add KEY        # Add env var
vercel logs               # View logs
vercel domains            # Manage domains
```

### Render Commands

```bash
render login              # Login
render deploy             # Deploy
render services           # List services
render logs SERVICE_ID    # View logs
render env set KEY=VALUE  # Set env var
```

---

## What You'll Get

After running all commands:

- ✅ **Frontend:** `https://infra-knowledge-graph-xyz.vercel.app`
- ✅ **Backend:** `https://infra-knowledge-graph-api.onrender.com`
- ✅ **Database:** PostgreSQL on Render (auto-linked)
- ✅ **Auto-deploy:** Both platforms watch GitHub for changes
- ✅ **HTTPS:** Automatic SSL certificates
- ✅ **Monitoring:** Built-in logs and analytics

---

## Cost

- **Vercel:** Free (unlimited deployments)
- **Render:** Free (with 15-min cold starts)
- **Total:** $0/month

---

## Next Steps

1. Test your deployment
2. Submit a test repository
3. Verify graph visualization works
4. Check logs if any issues
5. Share your live URL!

Need help? Check logs:
- Vercel: `vercel logs`
- Render: Dashboard → Your Service → Logs