# 🚀 Complete Deployment Guide

## Overview
This guide covers deploying both backend (Fly.io) and frontend (Vercel) for the AI Code Converter.

---

## 🔧 Backend Deployment (Fly.io)

### Quick Deploy
```bash
cd backend

# Install Fly CLI (if not installed)
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch and deploy
flyctl launch

# Set secrets
flyctl secrets set AI_PROVIDER=groq
flyctl secrets set GROQ_API_KEY=your_groq_api_key
flyctl secrets set CORS_ORIGINS="http://localhost:5173,https://your-app.vercel.app"

# Deploy
flyctl deploy
```

### Or Use Automated Script
```bash
cd backend
./deploy.sh
```

### Get Your Backend URL
```bash
flyctl info
# Look for: Hostname: your-app-name.fly.dev
```

---

## 🎨 Frontend Deployment (Vercel)

### Quick Deploy
```bash
cd frontend

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variable
vercel env add VITE_API_URL production
# Enter: https://your-app-name.fly.dev

# Deploy to production
vercel --prod
```

### Or Deploy via GitHub
1. Push code to GitHub
2. Go to https://vercel.com/new
3. Import repository
4. Set root directory: `frontend`
5. Add environment variable:
   - Key: `VITE_API_URL`
   - Value: `https://your-app-name.fly.dev`
6. Deploy

---

## 🔄 Post-Deployment Steps

### 1. Update Backend CORS
After getting your Vercel URL, update backend:
```bash
cd backend
flyctl secrets set CORS_ORIGINS="http://localhost:5173,https://your-app.vercel.app"
```

### 2. Test Your Application
1. Visit your Vercel URL
2. Upload a code file
3. Select source and target languages
4. Click "Convert Code"
5. Verify conversion works

### 3. Monitor Both Services

**Backend (Fly.io):**
```bash
flyctl logs
flyctl status
flyctl dashboard
```

**Frontend (Vercel):**
- Visit: https://vercel.com/dashboard
- Check deployments, logs, and analytics

---

## 📊 Architecture

```
┌─────────────────┐
│  User Browser   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vercel         │
│  (Frontend)     │
│  Vue.js + Vite  │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  Fly.io         │
│  (Backend)      │
│  FastAPI        │
└────────┬────────┘
         │ API
         ▼
┌─────────────────┐
│  AI Provider    │
│  Groq/OpenAI    │
└─────────────────┘
```

---

## 💰 Cost Estimates

### Fly.io (Backend)
- **Free Tier**: 3 shared-cpu-1x VMs with 256MB RAM
- **Auto-stop**: No cost when idle
- **Estimated**: $0-5/month for light usage

### Vercel (Frontend)
- **Hobby Plan**: Free
- **Bandwidth**: 100GB/month
- **Builds**: Unlimited
- **Estimated**: $0/month

### AI APIs
- **Groq**: Free tier available (recommended)
- **OpenAI**: Pay per token (~$0.50-2/1M tokens)
- **HuggingFace**: Free tier available

---

## 🔐 Security Checklist

- ✅ API keys stored as secrets (not in code)
- ✅ CORS properly configured
- ✅ HTTPS enforced on both services
- ✅ Environment variables separated by environment
- ✅ No sensitive data in frontend
- ✅ Input validation on backend
- ✅ Rate limiting (consider adding)

---

## 🐛 Troubleshooting

### Backend Issues
```bash
# Check logs
flyctl logs

# Check status
flyctl status

# Restart app
flyctl apps restart

# SSH into machine
flyctl ssh console
```

### Frontend Issues
```bash
# Check build logs in Vercel dashboard
# Verify environment variables
# Test API connection in browser console
```

### CORS Errors
- Verify backend CORS_ORIGINS includes frontend URL
- Check for trailing slashes
- Ensure HTTPS is used in production

### API Key Errors
```bash
# Verify secrets are set
flyctl secrets list

# Update if needed
flyctl secrets set GROQ_API_KEY=new_key
```

---

## 🔄 Updating Your App

### Backend Updates
```bash
cd backend
# Make changes
flyctl deploy
```

### Frontend Updates
```bash
cd frontend
# Make changes
git push  # Auto-deploys if connected to GitHub
# OR
vercel --prod
```

---

## 📚 Additional Resources

- **Fly.io Docs**: https://fly.io/docs
- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Vue.js Docs**: https://vuejs.org

---

## 🎉 Success!

Your AI Code Converter is now live and accessible worldwide!

**Backend**: https://your-app-name.fly.dev
**Frontend**: https://your-app.vercel.app

Share it with the world! 🌍
