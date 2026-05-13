# Step-by-Step Deployment Guide

Follow these exact steps to deploy your Infrastructure Knowledge Graph application.

## Prerequisites

- Git installed and configured
- GitHub account with repository access
- Vercel account (https://vercel.com/khuzaima05s-projects)
- Railway or Render account (for backend)

## Step 1: Push to GitHub

Open your terminal and run:

```bash
# Navigate to project root
cd /Users/khuzaimashakeel/Desktop/Infra-Knowledge-Graph

# Add all files
git add .

# Commit changes
git commit -m "Production-ready: IBM Cloud Infrastructure Knowledge Graph"

# Push to GitHub
git push origin main
```

**Verify:** Check https://github.com/Khuzaima05/Infra-Knowledge-Graph to ensure all files are pushed.

## Step 2: Deploy Backend (Choose One)

### Option A: Railway (Recommended)

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
```

2. **Login to Railway:**
```bash
railway login
```

3. **Deploy Backend:**
```bash
cd backend
railway init
railway add postgresql
railway up
```

4. **Get Backend URL:**
```bash
railway status
```
Copy the URL (e.g., `https://your-app.railway.app`)

5. **Set Environment Variables:**
```bash
railway variables set CORS_ORIGINS=https://your-app.vercel.app
```

### Option B: Render

1. Go to https://render.com
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository: `Khuzaima05/Infra-Knowledge-Graph`
4. Render will auto-deploy using `render.yaml`
5. Once deployed, copy the backend URL from Render dashboard

## Step 3: Deploy Frontend to Vercel

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Login to Vercel:**
```bash
vercel login
```
Use your account: khuzaima05s-projects

3. **Deploy Frontend:**
```bash
cd frontend

# Set environment variable
echo "NEXT_PUBLIC_API_URL=https://your-backend-url.com" > .env.production

# Deploy
vercel --prod
```

4. **Configure in Vercel Dashboard:**
   - Go to https://vercel.com/khuzaima05s-projects
   - Select your project
   - Go to Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL` = `https://your-backend-url.com`
   - Redeploy if needed

## Step 4: Update Backend CORS

After frontend is deployed, update backend CORS settings:

**Railway:**
```bash
cd backend
railway variables set CORS_ORIGINS=https://your-app.vercel.app
```

**Render:**
- Go to Render dashboard
- Select your service
- Environment → Add: `CORS_ORIGINS=https://your-app.vercel.app`
- Save and redeploy

## Step 5: Initialize Database

```bash
# If using Railway
railway run python scripts/init_db.py

# If using Render
# SSH into your service and run:
python scripts/init_db.py
```

## Step 6: Test Deployment

1. **Open your Vercel URL** (e.g., https://infra-knowledge-graph.vercel.app)
2. **Test Repository Analysis:**
   - Click "Add Repository"
   - Enter: `https://github.com/terraform-ibm-modules/terraform-ibm-landing-zone-vpc`
   - Click "Analyze Repository"
   - Wait for analysis to complete
   - View dependency graph

3. **Check Backend Health:**
   - Visit: `https://your-backend-url.com/health`
   - Should return: `{"status": "healthy"}`

4. **Check API Docs:**
   - Visit: `https://your-backend-url.com/docs`
   - Should show FastAPI documentation

## Troubleshooting

### CORS Errors

**Problem:** Frontend can't connect to backend

**Solution:**
```bash
# Update CORS_ORIGINS to include your Vercel URL
railway variables set CORS_ORIGINS=https://your-app.vercel.app
```

### Database Connection Errors

**Problem:** Backend can't connect to database

**Solution:**
- Check DATABASE_URL is set correctly
- Verify PostgreSQL is running
- Run database initialization: `python scripts/init_db.py`

### Build Failures

**Problem:** Vercel build fails

**Solution:**
- Check `package.json` has all dependencies
- Verify Node.js version compatibility
- Review build logs in Vercel dashboard

## Quick Commands Reference

```bash
# Push to GitHub
git add . && git commit -m "Update" && git push origin main

# Deploy backend (Railway)
cd backend && railway up

# Deploy frontend (Vercel)
cd frontend && vercel --prod

# View backend logs (Railway)
railway logs

# View frontend logs
# Check Vercel dashboard

# Update environment variables (Railway)
railway variables set KEY=value

# Restart backend (Railway)
railway restart
```

## Post-Deployment Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] Database initialized
- [ ] CORS configured correctly
- [ ] Environment variables set
- [ ] Health check passes
- [ ] Test repository analysis works
- [ ] Graph visualization loads
- [ ] Search functionality works
- [ ] Architecture summary generates

## Support

If you encounter issues:
1. Check logs (Railway: `railway logs`, Vercel: dashboard)
2. Verify environment variables
3. Test backend health endpoint
4. Review DEPLOYMENT.md for detailed troubleshooting

## URLs to Save

After deployment, save these URLs:

- **GitHub Repo**: https://github.com/Khuzaima05/Infra-Knowledge-Graph
- **Frontend (Vercel)**: https://your-app.vercel.app
- **Backend (Railway/Render)**: https://your-backend.railway.app
- **API Docs**: https://your-backend.railway.app/docs
- **Health Check**: https://your-backend.railway.app/health

---

**Ready to deploy!** Run the commands above in order, and your application will be live.