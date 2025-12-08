# Vercel Deployment Guide

## Prerequisites
- Vercel account (sign up at https://vercel.com)
- Backend deployed (e.g., on Fly.io, Railway, or Render)

## Deployment Steps

### Option 1: Deploy via Vercel CLI

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Login to Vercel**
```bash
vercel login
```

3. **Deploy from frontend directory**
```bash
cd frontend
vercel
```

4. **Set Environment Variable**
```bash
vercel env add VITE_API_URL production
# Enter your backend URL: https://your-backend-url.fly.dev
```

5. **Deploy to Production**
```bash
vercel --prod
```

### Option 2: Deploy via Vercel Dashboard

1. **Connect Repository**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Select the `frontend` directory as root

2. **Configure Build Settings**
   - Framework Preset: `Vite`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

3. **Add Environment Variables**
   - Go to Project Settings → Environment Variables
   - Add: `VITE_API_URL` = `https://your-backend-url.fly.dev`

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete

## Post-Deployment

### Update Backend CORS
Update your backend `.env` file to include your Vercel URL:
```env
CORS_ORIGINS=http://localhost:5173,https://your-app.vercel.app
```

### Test Your Deployment
1. Visit your Vercel URL
2. Try uploading a code file
3. Test code conversion
4. Check browser console for errors

## Troubleshooting

### Build Fails
- Check Node.js version (should be 18+)
- Verify all dependencies are in `package.json`
- Check build logs in Vercel dashboard

### API Connection Issues
- Verify `VITE_API_URL` environment variable
- Check backend CORS settings
- Ensure backend is running and accessible

### 404 Errors on Refresh
- Verify `vercel.json` rewrites configuration exists
- Check that SPA routing is properly configured

## Custom Domain (Optional)
1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions
4. Update backend CORS with new domain

## Automatic Deployments
- Push to `main` branch → Auto-deploy to production
- Push to other branches → Auto-deploy preview URLs
- Pull requests → Auto-deploy preview URLs

## Monitoring
- View deployment logs: Vercel Dashboard → Deployments
- Check analytics: Vercel Dashboard → Analytics
- Monitor errors: Vercel Dashboard → Logs
