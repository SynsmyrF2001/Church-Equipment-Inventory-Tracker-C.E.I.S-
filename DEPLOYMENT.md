# Deployment Guide

This guide covers different deployment options for the Church Equipment Inventory System.

## 🚀 Quick Deployment Options

### 1. Local Development
```bash
# Clone and setup
git clone https://github.com/yourusername/church-inventory-tracker.git
cd church-inventory-tracker
pip install -r requirements.txt

# Set environment variables
export SESSION_SECRET="your-secret-key"
export FLASK_ENV=development

# Initialize database and run
python -c "from app import app, db; app.app_context().push(); db.create_all()"
python app.py
```

### 2. Docker Deployment
```bash
# Build the image
docker build -t church-inventory .

# Run the container
docker run -p 8000:8000 \
  -e SESSION_SECRET="your-secret-key" \
  -e DATABASE_URL="sqlite:///church_inventory.db" \
  church-inventory
```

### 3. Heroku Deployment
```bash
# Install Heroku CLI and login
heroku login

# Create Heroku app
heroku create your-church-inventory-app

# Set environment variables
heroku config:set SESSION_SECRET="your-secret-key"
heroku config:set DATABASE_URL="postgresql://..."

# Deploy
git push heroku main

# Open the app
heroku open
```

## 🏗️ Production Deployment

### Prerequisites
- Python 3.11+
- PostgreSQL (recommended) or SQLite
- Web server (Nginx, Apache)
- WSGI server (Gunicorn, uWSGI)

### Step-by-Step Production Setup

#### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib

# Create application user
sudo useradd -m -s /bin/bash churchapp
sudo usermod -aG sudo churchapp
```

#### 2. Application Setup
```bash
# Switch to application user
sudo su - churchapp

# Clone repository
git clone https://github.com/yourusername/church-inventory-tracker.git
cd church-inventory-tracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Database Setup
```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE church_inventory;
CREATE USER churchapp WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE church_inventory TO churchapp;
\q

# Set database URL
export DATABASE_URL="postgresql://churchapp:your_password@localhost/church_inventory"
```

#### 4. Environment Configuration
```bash
# Create environment file
cat > .env << EOF
SESSION_SECRET=your-very-secure-secret-key
DATABASE_URL=postgresql://churchapp:your_password@localhost/church_inventory
FLASK_ENV=production
DEBUG=False
EOF
```

#### 5. Gunicorn Configuration
```bash
# Create Gunicorn config
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
EOF
```

#### 6. Systemd Service
```bash
# Create systemd service file
sudo tee /etc/systemd/system/church-inventory.service << EOF
[Unit]
Description=Church Inventory System
After=network.target

[Service]
User=churchapp
Group=churchapp
WorkingDirectory=/home/churchapp/church-inventory-tracker
Environment=PATH=/home/churchapp/church-inventory-tracker/venv/bin
Environment=DATABASE_URL=postgresql://churchapp:your_password@localhost/church_inventory
Environment=SESSION_SECRET=your-very-secure-secret-key
Environment=FLASK_ENV=production
ExecStart=/home/churchapp/church-inventory-tracker/venv/bin/gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable church-inventory
sudo systemctl start church-inventory
```

#### 7. Nginx Configuration
```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/church-inventory << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /home/churchapp/church-inventory-tracker/static;
        expires 30d;
    }
}
EOF

# Enable site and restart Nginx
sudo ln -s /etc/nginx/sites-available/church-inventory /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 8. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Set up auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔧 Configuration Options

### Environment Variables
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SESSION_SECRET` | Secret key for sessions | None | Yes |
| `DATABASE_URL` | Database connection string | SQLite | No |
| `FLASK_ENV` | Flask environment | production | No |
| `DEBUG` | Debug mode | False | No |
| `LOG_LEVEL` | Logging level | INFO | No |

### Database Configuration
```python
# SQLite (default)
DATABASE_URL = "sqlite:///church_inventory.db"

# PostgreSQL
DATABASE_URL = "postgresql://user:password@localhost/dbname"

# MySQL
DATABASE_URL = "mysql://user:password@localhost/dbname"
```

## 📊 Monitoring and Maintenance

### Log Monitoring
```bash
# View application logs
sudo journalctl -u church-inventory -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Backup
```bash
# PostgreSQL backup
pg_dump church_inventory > backup_$(date +%Y%m%d).sql

# SQLite backup
cp church_inventory.db backup_$(date +%Y%m%d).db
```

### Application Updates
```bash
# Pull latest changes
cd /home/churchapp/church-inventory-tracker
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart church-inventory
```

## 🔒 Security Considerations

### Production Security Checklist
- [ ] Use strong SESSION_SECRET
- [ ] Enable HTTPS with SSL certificate
- [ ] Configure firewall rules
- [ ] Use non-root user for application
- [ ] Regular security updates
- [ ] Database connection encryption
- [ ] Input validation and sanitization
- [ ] Rate limiting (consider using Flask-Limiter)

### Firewall Configuration
```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## 🆘 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check service status
sudo systemctl status church-inventory

# Check logs
sudo journalctl -u church-inventory -n 50
```

#### Database Connection Issues
```bash
# Test database connection
psql $DATABASE_URL -c "SELECT 1;"

# Check PostgreSQL status
sudo systemctl status postgresql
```

#### Static Files Not Loading
```bash
# Check file permissions
ls -la /home/churchapp/church-inventory-tracker/static/

# Check Nginx configuration
sudo nginx -t
```

## 📞 Support

For deployment issues:
1. Check the logs for error messages
2. Verify environment variables are set correctly
3. Ensure all dependencies are installed
4. Open an issue on GitHub with detailed error information 