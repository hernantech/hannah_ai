# DigitalOcean Deployment Guide

## Option 1: App Platform (Recommended - Simplest)

### Prerequisites
```bash
# Install doctl
brew install doctl  # macOS
# or download from: https://docs.digitalocean.com/reference/doctl/how-to/install/

# Authenticate
doctl auth init
```

### Deploy via CLI

#### A. Deploy from GitHub (Easiest)
```bash
# 1. Push your code to GitHub first
git add .
git commit -m "Prepare for deployment"
git push origin main

# 2. Create app from spec file
doctl apps create --spec backend/.do/app.yaml

# 3. Set your FAL_KEY secret
doctl apps update YOUR_APP_ID --env FAL_KEY=your_fal_key_here
```

#### B. Deploy from Local Container
```bash
# 1. Build your container
cd backend
docker build -t hannah-backend .

# 2. Push to DigitalOcean Container Registry
# Create registry first
doctl registry create hannah-registry

# Login to registry
doctl registry login

# Tag and push
docker tag hannah-backend registry.digitalocean.com/hannah-registry/backend:latest
docker push registry.digitalocean.com/hannah-registry/backend:latest

# 3. Create app pointing to registry
doctl apps create --spec .do/app.yaml
```

### Deploy via UI (Even Simpler)
1. Go to https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Choose source:
   - **From GitHub**: Connect repo, select `backend` folder
   - **From Container**: Use DigitalOcean Container Registry
4. DO will auto-detect your Dockerfile
5. Set environment variables:
   - `FAL_KEY` (your fal.ai API key)
   - `FLASK_ENV=production`
6. Review and deploy!

### Update Production CMD
Before deploying, update your Dockerfile to use gunicorn:

```dockerfile
# Change line 33 in Dockerfile from:
CMD ["python", "app.py"]

# To:
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
```

### Estimated Costs
- **Basic XXS**: $5/month (512 MB RAM, 1 vCPU)
- **Basic XS**: $12/month (1 GB RAM, 1 vCPU) - Better for production
- **Basic S**: $24/month (2 GB RAM, 2 vCPU) - If you get traffic

### Post-Deployment
```bash
# View apps
doctl apps list

# Get app info
doctl apps get YOUR_APP_ID

# View logs
doctl apps logs YOUR_APP_ID --type RUN

# Update app
doctl apps update YOUR_APP_ID --spec backend/.do/app.yaml
```

---

## Option 2: Simple Droplet + Docker (More Control)

If you prefer a traditional VM approach:

### Setup
```bash
# 1. Create a Droplet (US West - San Francisco)
doctl compute droplet create hannah-backend \
  --image docker-20-04 \
  --size s-1vcpu-1gb \
  --region sfo3 \
  --ssh-keys YOUR_SSH_KEY_ID

# 2. Get droplet IP
doctl compute droplet list

# 3. SSH into droplet
ssh root@YOUR_DROPLET_IP

# 4. Clone your repo or copy files
git clone YOUR_REPO_URL
cd hannah/backend

# 5. Create .env file with your secrets
cat > .env << EOF
FAL_KEY=your_fal_key_here
FLASK_ENV=production
EOF

# 6. Update docker-compose for production
# 7. Run with docker-compose
docker-compose up -d

# 8. Setup firewall
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable

# 9. Setup nginx reverse proxy (optional but recommended)
# This gives you SSL and proper domain routing
```

### Costs
- **Basic Droplet**: $6/month (1GB RAM, 1 vCPU, 25GB SSD)
- **Recommended**: $12/month (2GB RAM, 1 vCPU, 50GB SSD)

---

## Recommendation

**Use App Platform** because:
1. ✅ Zero networking setup - it handles everything
2. ✅ Automatic HTTPS/SSL
3. ✅ Auto-deploy from GitHub
4. ✅ Built-in monitoring and logs
5. ✅ Easy rollbacks
6. ✅ No server management

**Use Droplet** only if:
- You need full control
- You want to run multiple services
- You're comfortable with DevOps

---

## Quick Start Commands

### Fastest Path to Production:
```bash
# 1. Update Dockerfile for production
sed -i '' 's/CMD \["python", "app.py"\]/CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]/' backend/Dockerfile

# 2. Deploy via doctl
cd backend
doctl apps create --spec .do/app.yaml

# 3. Get your app URL
doctl apps list
# Visit: https://hannah-backend-xxxxx.ondigitalocean.app
```

---

## Environment Variables to Set
- `FAL_KEY` - Your fal.ai API key (SECRET)
- `FLASK_ENV` - Set to `production`
- Any other API keys your app needs
