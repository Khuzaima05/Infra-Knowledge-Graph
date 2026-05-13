# Vercel Deployment Guide

## Problem: Monorepo Detection Error

Vercel detected your monorepo structure (frontend + backend) and requires configuration. I've created the necessary files.

## Solution: Deploy Separately

**Don't use the root-level deployment.** Deploy frontend and backend as separate projects.

---

## Step 1: Deploy Frontend Only

### Option A: Via Vercel Dashboard (Easiest)

1. Go to https://vercel.com/new
2. Import your GitHub repo: `Khuzaima05/Infra-Knowledge-Graph`
3. **Configure Project:**
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend` ← IMPORTANT!
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
4. **Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.vercel.app
   ```
5. Click **Deploy**

### Option B: Via CLI

```bash
cd frontend
vercel --prod
# Follow prompts, it will auto-detect Next.js
```

---

## Step 2: Deploy Backend Separately

### ⚠️ Important: Vercel Limitations for FastAPI

Vercel's Python runtime has limitations:
- ❌ No persistent file storage (cloned repos will be lost)
- ❌ No background tasks (analysis will fail)
- ❌ No SQLite (need external PostgreSQL)
- ❌ 10-second timeout (large repos will fail)

### Recommended: Use Render for Backend

**Render is better for FastAPI:**
- ✅ Persistent storage
- ✅ Background tasks work
- ✅ Free PostgreSQL included
- ✅ No timeouts

#### Deploy Backend on Render:

1. Go to https://render.com/dashboard
2. Click **New +** → **Web Service**
3. Connect GitHub: `Khuzaima05/Infra-Knowledge-Graph`
4. **Configure:**
   - **Name:** `infra-knowledge-graph-api`
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables:**
   ```
   DATABASE_URL=postgresql://...  (auto-provided by Render)
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```
6. Click **Create Web Service**
7. Add PostgreSQL:
   - Go to **Dashboard** → **New +** → **PostgreSQL**
   - Link it to your web service

---

## Step 3: Connect Frontend to Backend

1. Get your Render backend URL: `https://infra-knowledge-graph-api.onrender.com`
2. Update Vercel frontend environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://infra-knowledge-graph-api.onrender.com
   ```
3. Redeploy frontend (Vercel will auto-redeploy on env change)

---

## Step 4: Update Backend CORS

Update your backend environment on Render:
```
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

---

## Alternative: Deploy Both on Render

If you prefer everything on Render:

### Frontend on Render:
1. **New +** → **Static Site**
2. **Root Directory:** `frontend`
3. **Build Command:** `npm install && npm run build`
4. **Publish Directory:** `frontend/.next`

### Backend on Render:
(Same as above)

---

## Quick Commands

### Push to GitHub First:
```bash
git add .
git commit -m "Add Vercel configuration"
git push origin main
```

### Deploy Frontend (Vercel):
```bash
cd frontend
vercel --prod
```

### Deploy Backend (Render):
```bash
# Use Render dashboard - it's easier than CLI
# https://render.com/dashboard
```

---

## Testing After Deployment

1. **Frontend:** Visit your Vercel URL
2. **Backend Health:** `https://your-backend.onrender.com/health`
3. **API Docs:** `https://your-backend.onrender.com/docs`
4. **Test Analysis:** Submit a repo URL in the frontend

---

## Troubleshooting

### Frontend can't reach backend:
- Check `NEXT_PUBLIC_API_URL` in Vercel environment variables
- Verify CORS settings in backend

### Backend errors:
- Check Render logs: Dashboard → Your Service → Logs
- Verify DATABASE_URL is set
- Ensure PostgreSQL is linked

### Cold starts (Render free tier):
- First request after 15 min takes 30-60 seconds
- This is normal for free tier
- Upgrade to paid tier ($7/month) for always-on

---

## Cost Summary

### Free Tier (Recommended):
- **Vercel Frontend:** Free (unlimited)
- **Render Backend:** Free (with cold starts)
- **Render PostgreSQL:** Free (1GB storage)
- **Total:** $0/month

### Paid Tier (Production):
- **Vercel Frontend:** Free
- **Render Backend:** $7/month (always-on)
- **Render PostgreSQL:** Free
- **Total:** $7/month

---

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Deploy backend on Render
3. ✅ Deploy frontend on Vercel
4. ✅ Update environment variables
5. ✅ Test with IBM Cloud repos

Need help? Check the logs in Render/Vercel dashboards.