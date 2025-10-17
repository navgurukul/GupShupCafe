# Python FastAPI Backend - AWS EC2 Deployment Guide

## Prerequisites
- AWS Account
- EC2 instance (Ubuntu 20.04/22.04 LTS recommended)
- Domain name (optional, for production)
- SSH key pair for EC2 access

## EC2 Instance Setup

### 1. Launch EC2 Instance

1. **Go to AWS EC2 Console**
2. **Launch Instance** with the following settings:
   - **Name**: gupshup-cafe-api
   - **AMI**: Ubuntu Server 22.04 LTS
   - **Instance Type**: t2.micro (free tier) or t2.small for production
   - **Key pair**: Create or select existing key pair
   - **Network settings**: 
     - Allow SSH (port 22) from your IP
     - Allow HTTP (port 80) from anywhere
     - Allow HTTPS (port 443) from anywhere
     - Allow Custom TCP (port 3003) from anywhere (or use nginx reverse proxy)
   - **Storage**: 8-20 GB gp3

3. **Launch instance** and wait for it to be running

### 2. Connect to EC2 Instance

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### 3. Install Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.11 and pip
sudo apt install -y python3.11 python3.11-venv python3-pip git

# Install nginx (optional, for reverse proxy)
sudo apt install -y nginx
```

### 4. Clone and Setup Application

```bash
# Clone repository
cd /home/ubuntu
git clone https://github.com/navgurukul/GupShupCafe.git
cd GupShupCafe/server_py

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Configure Environment Variables

```bash
# Create .env file
nano .env
```

Add the following:
```env
PORT=3003
PYTHON_ENV=production

# CORS - Add your frontend domain
ALLOWED_ORIGINS=https://your-frontend-domain.com,https://gup-shup-cafe.vercel.app

# Database
DATABASE_URL=/home/ubuntu/GupShupCafe/server_py/data/roundtable.db

# AI Configuration
HUGGINGFACE_API_KEY=your_api_key_here
HUGGINGFACE_MODEL=microsoft/DialoGPT-medium

# Discussion Settings
DEFAULT_SPEAKING_TIME=60
MIN_PARTICIPANTS=1
MAX_PARTICIPANTS=8

SESSION_TIMEOUT=3600000
```

### 6. Setup Systemd Service

```bash
# Copy service file
sudo cp gupshup-api.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable gupshup-api

# Start service
sudo systemctl start gupshup-api

# Check status
sudo systemctl status gupshup-api
```

### 7. Configure Nginx Reverse Proxy (Optional but Recommended)

```bash
# Create nginx configuration
sudo nano /etc/nginx/sites-available/gupshup-api
```

Add the following:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # or use EC2 public IP

    location / {
        proxy_pass http://127.0.0.1:3003;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io/ {
        proxy_pass http://127.0.0.1:3003/socket.io/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/gupshup-api /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### 8. Setup SSL with Let's Encrypt (Optional but Recommended)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is setup automatically
```

## Docker Deployment (Alternative)

### 1. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Logout and login again, or run:
newgrp docker
```

### 2. Build and Run Container

```bash
# Build Docker image
cd /home/ubuntu/GupShupCafe/server_py
docker build -t gupshup-api .

# Run container
docker run -d \
  --name gupshup-api \
  --restart unless-stopped \
  -p 3003:3003 \
  -v /home/ubuntu/GupShupCafe/server_py/data:/app/data \
  -v /home/ubuntu/GupShupCafe/server_py/.env:/app/.env \
  gupshup-api
```

### 3. Manage Container

```bash
# Check logs
docker logs gupshup-api

# Stop container
docker stop gupshup-api

# Start container
docker start gupshup-api

# Remove container
docker rm -f gupshup-api
```

## Monitoring and Maintenance

### View Logs

```bash
# Systemd service logs
sudo journalctl -u gupshup-api -f

# Or if using Docker
docker logs -f gupshup-api
```

### Update Application

```bash
# Pull latest code
cd /home/ubuntu/GupShupCafe
git pull origin main

# Restart service
sudo systemctl restart gupshup-api

# Or if using Docker
docker stop gupshup-api
docker rm gupshup-api
docker build -t gupshup-api .
docker run -d --name gupshup-api --restart unless-stopped -p 3003:3003 \
  -v /home/ubuntu/GupShupCafe/server_py/data:/app/data \
  -v /home/ubuntu/GupShupCafe/server_py/.env:/app/.env \
  gupshup-api
```

### Database Backup

```bash
# Backup SQLite database
cp /home/ubuntu/GupShupCafe/server_py/data/roundtable.db \
   /home/ubuntu/backups/roundtable-$(date +%Y%m%d).db
```

## Security Best Practices

1. **Keep system updated**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Configure firewall**:
   ```bash
   sudo ufw enable
   sudo ufw allow 22    # SSH
   sudo ufw allow 80    # HTTP
   sudo ufw allow 443   # HTTPS
   sudo ufw allow 3003  # API (if not using nginx)
   ```

3. **Use strong environment variables** - Never commit .env files

4. **Regular backups** - Setup automated database backups

5. **Monitor logs** - Check for unusual activity

## Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u gupshup-api -n 50

# Check if port is already in use
sudo lsof -i :3003
```

### Database errors
```bash
# Check database file permissions
ls -la /home/ubuntu/GupShupCafe/server_py/data/

# Ensure write permissions
chmod 755 /home/ubuntu/GupShupCafe/server_py/data/
chmod 644 /home/ubuntu/GupShupCafe/server_py/data/roundtable.db
```

### CORS errors
- Verify ALLOWED_ORIGINS in .env includes your frontend domain
- Check nginx proxy headers if using reverse proxy

## Cost Optimization

- **t2.micro** (free tier): Good for testing, limited traffic
- **t2.small**: Suitable for moderate traffic
- Use **Reserved Instances** for long-term deployments
- Setup **Auto Scaling** for variable traffic

## Support

For issues or questions:
- GitHub Issues: https://github.com/navgurukul/GupShupCafe/issues
- Documentation: See main README.md
