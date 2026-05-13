# Deployment Guide

Complete guide for deploying the Infrastructure Knowledge Graph application to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
5. [Database Setup](#database-setup)
6. [Production Configuration](#production-configuration)
7. [Monitoring & Logging](#monitoring--logging)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+ (or SQLite for development)
- Git
- Docker (optional, for containerized deployment)

### Required Accounts
- GitHub account (for repository access)
- Vercel account (for frontend hosting)
- Railway/Render/Heroku account (for backend hosting, optional)

## Environment Setup

### Backend Environment Variables

Create `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/infra_kg
# Or for SQLite: sqlite:///./infra_kg.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

# CORS Origins (comma-separated)
CORS_ORIGINS=https://your-frontend-domain.vercel.app,https://www.your-domain.com

# Storage
CLONED_REPOS_DIR=./cloned_repos
MAX_REPO_SIZE_MB=500

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# Security
SECRET_KEY=your-secret-key-here-change-in-production
```

### Frontend Environment Variables

Create `frontend/.env.production`:

```bash
NEXT_PUBLIC_API_URL=https://your-backend-api.com
```

## Backend Deployment

### Option 1: Railway (Recommended)

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
```

2. **Login to Railway:**
```bash
railway login
```

3. **Initialize Project:**
```bash
cd backend
railway init
```

4. **Add PostgreSQL:**
```bash
railway add postgresql
```

5. **Set Environment Variables:**
```bash
railway variables set DATABASE_URL=${{RAILWAY_POSTGRES_URL}}
railway variables set CORS_ORIGINS=https://your-app.vercel.app
```

6. **Deploy:**
```bash
railway up
```

### Option 2: Render

1. **Create `render.yaml`:**
```yaml
services:
  - type: web
    name: infra-kg-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: infra-kg-db
          property: connectionString
      - key: PYTHON_VERSION
        value: 3.11.0

databases:
  - name: infra-kg-db
    databaseName: infra_kg
    user: infra_kg_user
```

2. **Connect Repository:**
- Go to render.com
- Click "New +" → "Blueprint"
- Connect your GitHub repository
- Render will auto-deploy using render.yaml

### Option 3: Docker

1. **Build Image:**
```bash
cd backend
docker build -t infra-kg-api .
```

2. **Run Container:**
```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host/db \
  -e CORS_ORIGINS=https://your-app.vercel.app \
  --name infra-kg-api \
  infra-kg-api
```

### Option 4: Traditional VPS

1. **Install Dependencies:**
```bash
sudo apt update
sudo apt install python3.11 python3-pip postgresql nginx
```

2. **Setup Application:**
```bash
cd /opt
git clone https://github.com/Khuzaima05/Infra-Knowledge-Graph.git
cd Infra-Knowledge-Graph/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Create Systemd Service:**

Create `/etc/systemd/system/infra-kg.service`:
```ini
[Unit]
Description=Infrastructure Knowledge Graph API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/Infra-Knowledge-Graph/backend
Environment="PATH=/opt/Infra-Knowledge-Graph/backend/venv/bin"
ExecStart=/opt/Infra-Knowledge-Graph/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

4. **Start Service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable infra-kg
sudo systemctl start infra-kg
```

5. **Configure Nginx:**

Create `/etc/nginx/sites-available/infra-kg`:
```nginx
server {
    listen 80;
    server_name api.your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/infra-kg /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

6. **Setup SSL with Certbot:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.your-domain.com
```

## Frontend Deployment (Vercel)

### Step 1: Prepare Repository

1. **Ensure `.gitignore` is correct:**
```
# Frontend
frontend/node_modules/
frontend/.next/
frontend/out/
frontend/.env.local
frontend/.env.production

# Backend
backend/__pycache__/
backend/*.pyc
backend/venv/
backend/.env
backend/cloned_repos/
backend/logs/
backend/*.db
```

2. **Push to GitHub:**
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 2: Deploy to Vercel

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Login:**
```bash
vercel login
```

3. **Deploy:**
```bash
cd frontend
vercel
```

4. **Configure Project:**
- Framework Preset: Next.js
- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `.next`

5. **Set Environment Variables:**

In Vercel Dashboard:
- Go to Project Settings → Environment Variables
- Add: `NEXT_PUBLIC_API_URL` = `https://your-backend-api.com`

6. **Deploy to Production:**
```bash
vercel --prod
```

### Step 3: Custom Domain (Optional)

1. **Add Domain in Vercel:**
- Go to Project Settings → Domains
- Add your custom domain
- Follow DNS configuration instructions

2. **Update Backend CORS:**
```bash
# Add your custom domain to CORS_ORIGINS
railway variables set CORS_ORIGINS=https://your-custom-domain.com
```

## Database Setup

### PostgreSQL Production Setup

1. **Create Database:**
```sql
CREATE DATABASE infra_kg;
CREATE USER infra_kg_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE infra_kg TO infra_kg_user;
```

2. **Run Migrations:**
```bash
cd backend
python scripts/init_db.py
```

3. **Backup Strategy:**

Create backup script `/opt/scripts/backup-db.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump infra_kg > "$BACKUP_DIR/infra_kg_$TIMESTAMP.sql"
# Keep only last 7 days
find $BACKUP_DIR -name "infra_kg_*.sql" -mtime +7 -delete
```

Add to crontab:
```bash
0 2 * * * /opt/scripts/backup-db.sh
```

## Production Configuration

### Backend Optimizations

1. **Update `backend/config/settings.py`:**
```python
# Production settings
DEBUG = False
TESTING = False

# Worker configuration
WORKERS = 4  # (2 x CPU cores) + 1

# Connection pooling
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10

# Rate limiting
RATE_LIMIT_PER_MINUTE = 60
```

2. **Use Gunicorn:**
```bash
pip install gunicorn
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

### Frontend Optimizations

1. **Update `frontend/next.config.mjs`:**
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  compress: true,
  poweredByHeader: false,
  
  // Image optimization
  images: {
    domains: [],
    formats: ['image/webp', 'image/avif'],
  },
  
  // Performance
  swcMinify: true,
  
  // Security headers
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin'
          }
        ]
      }
    ]
  }
}

export default nextConfig
```

## Monitoring & Logging

### Backend Monitoring

1. **Setup Sentry (Error Tracking):**
```bash
pip install sentry-sdk
```

Add to `backend/app/main.py`:
```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=0.1,
    environment="production"
)
```

2. **Health Check Endpoint:**

Already implemented at `/health`

3. **Metrics Endpoint:**

Already implemented at `/metrics`

### Frontend Monitoring

1. **Vercel Analytics:**

Already enabled automatically

2. **Custom Error Tracking:**

Add to `frontend/app/layout.tsx`:
```typescript
import { useEffect } from 'react'

export default function RootLayout({ children }) {
  useEffect(() => {
    // Track errors
    window.addEventListener('error', (event) => {
      console.error('Global error:', event.error)
      // Send to your error tracking service
    })
  }, [])
  
  return children
}
```

## Troubleshooting

### Common Issues

#### 1. CORS Errors

**Problem:** Frontend can't connect to backend

**Solution:**
```bash
# Update backend CORS_ORIGINS
railway variables set CORS_ORIGINS=https://your-app.vercel.app
```

#### 2. Database Connection Errors

**Problem:** Can't connect to PostgreSQL

**Solution:**
- Check DATABASE_URL format
- Verify database is running
- Check firewall rules
- Test connection: `psql $DATABASE_URL`

#### 3. Build Failures

**Problem:** Vercel build fails

**Solution:**
- Check `package.json` scripts
- Verify all dependencies are listed
- Check Node.js version compatibility
- Review build logs in Vercel dashboard

#### 4. API Timeout

**Problem:** Requests timing out

**Solution:**
- Increase timeout in Vercel: Project Settings → Functions → Timeout
- Optimize slow queries
- Add caching layer
- Scale backend resources

### Health Checks

**Backend:**
```bash
curl https://your-api.com/health
```

**Frontend:**
```bash
curl https://your-app.vercel.app
```

### Logs

**Backend (Railway):**
```bash
railway logs
```

**Frontend (Vercel):**
- View in Vercel Dashboard → Deployments → Logs

## Post-Deployment Checklist

- [ ] Backend health check passes
- [ ] Frontend loads correctly
- [ ] API endpoints respond
- [ ] Database migrations applied
- [ ] Environment variables set
- [ ] CORS configured correctly
- [ ] SSL certificates active
- [ ] Monitoring enabled
- [ ] Backups configured
- [ ] Documentation updated
- [ ] Team notified

## Rollback Procedure

### Vercel (Frontend)

1. Go to Deployments
2. Find previous working deployment
3. Click "..." → "Promote to Production"

### Railway (Backend)

1. Go to Deployments
2. Find previous working deployment
3. Click "Redeploy"

### Manual Rollback

```bash
git revert HEAD
git push origin main
```

## Support

For deployment issues:
- GitHub Issues: https://github.com/Khuzaima05/Infra-Knowledge-Graph/issues
- Documentation: See README.md and other docs in repository

---

**Made with Bob** - Infrastructure Knowledge Graph Deployment Guide