# Railway Deployment Guide

This guide will help you deploy your Flask MFA application to Railway for free public access.

## Prerequisites

1. A GitHub account
2. A Railway account (sign up at [railway.app](https://railway.app))
3. Your code pushed to a GitHub repository

## Step-by-Step Deployment Instructions

### Step 1: Push Your Code to GitHub

1. If you haven't already, initialize a git repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Ready for Railway deployment"
   ```

2. Create a new repository on GitHub and push your code:
   ```bash
   git remote add origin <your-github-repo-url>
   git branch -M main
   git push -u origin main
   ```

### Step 2: Create a Railway Account

1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Sign up using your GitHub account (recommended for easy integration)

### Step 3: Deploy from GitHub

1. In Railway dashboard, click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Railway will automatically detect it's a Python/Flask app

### Step 4: Configure Environment Variables

1. In your Railway project, go to the "Variables" tab
2. Add the following environment variables:
   - `JWT_SECRET`: Generate a strong random secret (you can use: `openssl rand -hex 32`)
   - `PORT`: Railway automatically sets this, but you can verify it's set
   - `FLASK_ENV`: Set to `production` (optional, defaults to production)

   Example JWT_SECRET generation:
   ```bash
   # On Linux/Mac
   openssl rand -hex 32
   
   # Or use Python
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

### Step 5: Verify Deployment

1. Railway will automatically build and deploy your app
2. Once deployed, Railway will provide a public URL (e.g., `https://your-app-name.railway.app`)
3. Click on the URL to access your application
4. The frontend should load at the root URL

### Step 6: Test Your Deployment

1. Visit your Railway URL
2. Register a new user
3. Test login functionality
4. Test MFA setup and verification

## Important Notes

### Database Persistence

- The SQLite database (`auth_demo.db`) will be created in the backend-minimal-flask directory
- **Note**: SQLite files on Railway are ephemeral and may be lost during redeployments
- For production use, consider upgrading to Railway's PostgreSQL addon for persistent storage

### Static Files

- Frontend files (HTML, JS) are served directly by Flask
- The app is configured to serve static files from the `frontend/` directory

### Email OTP

- Currently, email OTPs are printed to the server console/logs
- To send real emails, configure SMTP settings and update the `send_email_otp` function in `auth_core.py`

### Security Considerations

1. **JWT Secret**: Always use a strong, random secret in production
2. **HTTPS**: Railway automatically provides HTTPS for your app
3. **CORS**: Currently configured to allow all origins. For production, restrict CORS to specific domains

## Troubleshooting

### Build Fails

- Check Railway build logs for errors
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility (runtime.txt specifies Python 3.11)

### App Won't Start

- Check Railway deployment logs
- Verify PORT environment variable is set (Railway sets this automatically)
- Ensure Procfile is in the root directory

### Database Issues

- SQLite files may be reset on redeploy
- Consider using Railway's PostgreSQL addon for persistent storage

### Static Files Not Loading

- Verify the frontend directory structure matches the code
- Check that `FRONTEND_DIR` path is correct in `server.py`

## Updating Your App

1. Make changes to your code
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your update message"
   git push
   ```
3. Railway will automatically detect the changes and redeploy

## Railway Free Tier Limits

- 512MB RAM
- 100 hours of usage per month (resets monthly)
- $5 free credit per month

## Getting Help

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Check Railway logs in your project dashboard

## Next Steps (Optional Enhancements)

1. **Add PostgreSQL**: Use Railway's PostgreSQL addon for persistent database
2. **Custom Domain**: Configure a custom domain in Railway project settings
3. **Email Service**: Integrate SendGrid or similar for real email OTPs
4. **Monitoring**: Set up Railway's monitoring and alerts
5. **CI/CD**: Railway automatically handles deployments from GitHub

---

Your app should now be live and publicly accessible! 🚀

