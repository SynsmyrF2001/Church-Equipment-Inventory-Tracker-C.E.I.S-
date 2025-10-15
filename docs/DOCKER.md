# 🐳 Docker Deployment Guide

Complete guide for running the Church Equipment Inventory System with Docker on your local machine or in production.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start - Local Development](#quick-start---local-development)
- [Running on Your Laptop](#running-on-your-laptop)
- [Production Deployment](#production-deployment)
- [Docker Commands Reference](#docker-commands-reference)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

1. **Docker Desktop** (macOS/Windows) or **Docker Engine** (Linux)
   - Download from: https://www.docker.com/products/docker-desktop
   - Minimum version: Docker 20.10+, Docker Compose v2.0+

2. **Verify Installation**
   ```bash
   docker --version
   docker-compose --version
   ```

---

## Quick Start - Local Development

### Option 1: Full Stack with PostgreSQL (Recommended)

This runs the complete application with a PostgreSQL database in containers.

```bash
# 1. Clone/Navigate to project directory
cd ChurchInventoryTracker

# 2. Create environment file
cp env.example .env

# 3. Generate a secure session secret
python3 -c 'import secrets; print(secrets.token_hex(32))'
# Copy the output and update SESSION_SECRET in .env file

# 4. Build and start all services
docker-compose up --build

# 5. Access the application
# Open your browser to: http://localhost:5000
```

That's it! The application is now running on your laptop at `http://localhost:5000`.

### Option 2: Application Only (Uses SQLite)

If you just want to run the Flask app without PostgreSQL:

```bash
# Build the Docker image
docker build -t church-inventory .

# Run the container
docker run -d \
  -p 5000:5000 \
  -e SESSION_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))') \
  -e DATABASE_URL=sqlite:///church_inventory.db \
  -v $(pwd)/instance:/app/instance \
  --name church-inventory-app \
  church-inventory

# Access at http://localhost:5000
```

---

## Running on Your Laptop

### Step-by-Step Instructions

1. **Start the Application**
   ```bash
   cd "ChurchInventoryTracker"
   docker-compose up
   ```

2. **Watch the Logs**
   You'll see startup messages like:
   ```
   🚀 Church Equipment Inventory System - Starting...
   ⏳ Waiting for PostgreSQL to be ready...
   ✅ PostgreSQL is ready!
   🗄️  Initializing database...
   ✅ Database initialized successfully
   🎉 Startup complete! Starting application...
   ```

3. **Access the Application**
   - Open your web browser
   - Navigate to: `http://localhost:5000`
   - You should see the Church Inventory dashboard!

4. **Stop the Application**
   - Press `Ctrl+C` in the terminal, or
   - Run: `docker-compose down`

### Accessing Different Services

- **Web Application**: http://localhost:5000
- **PostgreSQL Database**: localhost:5432
  - Username: `church_admin`
  - Password: `changeme123` (change in .env file)
  - Database: `church_inventory`

### Development Mode

For active development with live code reloading:

```bash
# Run with volume mounts for live updates
docker-compose -f docker-compose.yml up --build

# Or run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f web
```

---

## Production Deployment

### 1. Prepare Production Environment

```bash
# Create production .env file
cp env.example .env

# Edit .env with production values:
nano .env
```

**Important Production Settings:**
```env
# Security
SESSION_SECRET=<generate-strong-64-char-secret>

# Database
DATABASE_URL=postgresql://user:password@db:5432/church_inventory
POSTGRES_PASSWORD=<strong-password>

# Flask
FLASK_ENV=production
DEBUG=False

# Optional: SMS notifications
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_phone_number
```

### 2. Deploy with SSL/HTTPS (Optional)

```bash
# Start with nginx reverse proxy
docker-compose --profile production up -d

# Get SSL certificates (Let's Encrypt)
# 1. Install certbot on your host
# 2. Obtain certificates
# 3. Mount them in docker-compose.yml under nginx volumes
```

### 3. Start Production Services

```bash
# Build and start in detached mode
docker-compose up -d --build

# Check service health
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Database Backups

```bash
# Backup database
docker-compose exec db pg_dump -U church_admin church_inventory > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T db psql -U church_admin church_inventory < backup_20241009.sql
```

---

## Docker Commands Reference

### Building and Starting

```bash
# Build images
docker-compose build

# Start services
docker-compose up

# Start in background (detached)
docker-compose up -d

# Rebuild and start
docker-compose up --build

# Start specific service
docker-compose up web
```

### Stopping and Removing

```bash
# Stop services (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove containers, networks, and volumes
docker-compose down -v

# Remove everything including images
docker-compose down --rmi all -v
```

### Viewing Logs

```bash
# View all logs
docker-compose logs

# Follow logs (real-time)
docker-compose logs -f

# View specific service logs
docker-compose logs web
docker-compose logs db

# Last 100 lines
docker-compose logs --tail=100
```

### Executing Commands

```bash
# Open shell in web container
docker-compose exec web bash

# Open shell in database container
docker-compose exec db bash

# Run Python commands
docker-compose exec web python -c "from app import app, db; print('Hello')"

# Access PostgreSQL CLI
docker-compose exec db psql -U church_admin -d church_inventory
```

### Managing Services

```bash
# Restart a service
docker-compose restart web

# View running services
docker-compose ps

# View service resource usage
docker stats

# Scale services (if supported)
docker-compose up -d --scale web=3
```

---

## Troubleshooting

### Issue: Port Already in Use

```bash
# Error: Bind for 0.0.0.0:5000 failed: port is already allocated

# Solution 1: Stop conflicting service
lsof -ti:5000 | xargs kill -9

# Solution 2: Change port in docker-compose.yml
# Edit ports section: "8080:5000" instead of "5000:5000"
```

### Issue: Database Connection Failed

```bash
# Check if database is ready
docker-compose logs db

# Restart database
docker-compose restart db

# Check database connection
docker-compose exec db pg_isready -U church_admin
```

### Issue: Permission Denied

```bash
# Fix volume permissions
sudo chown -R $(whoami):$(whoami) ./instance ./uploads

# Or run with sudo (not recommended)
sudo docker-compose up
```

### Issue: Container Keeps Restarting

```bash
# View logs for errors
docker-compose logs web

# Check health status
docker-compose ps

# Inspect container
docker inspect church_inventory_web
```

### Issue: Out of Disk Space

```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Clean everything
docker system prune -a --volumes
```

### Issue: Changes Not Reflected

```bash
# Rebuild without cache
docker-compose build --no-cache

# Remove old images and rebuild
docker-compose down --rmi all
docker-compose up --build
```

---

## Health Checks

### Application Health

```bash
# Check application health endpoint
curl http://localhost:5000/health

# Expected response:
# {"status":"healthy","database":"connected","version":"1.0.0"}
```

### Database Health

```bash
# Check PostgreSQL health
docker-compose exec db pg_isready -U church_admin
```

---

## Performance Tuning

### Optimize for Production

1. **Adjust Worker Count** (in docker-compose.yml)
   ```yaml
   command: gunicorn --workers 4 --worker-class sync app:app
   # Workers = (2 x CPU_CORES) + 1
   ```

2. **Database Connection Pool** (in app.py)
   ```python
   SQLALCHEMY_ENGINE_OPTIONS = {
       "pool_size": 10,
       "max_overflow": 20,
       "pool_recycle": 3600,
   }
   ```

3. **Enable Nginx Caching** (uncomment in nginx.conf)

---

## Updating the Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d

# Check logs
docker-compose logs -f web
```

---

## Security Best Practices

1. **Never commit .env files** - Add to .gitignore
2. **Use strong passwords** - Generate with: `openssl rand -base64 32`
3. **Update SESSION_SECRET** - Different for each environment
4. **Use HTTPS in production** - Set up SSL certificates
5. **Regular backups** - Automate database backups
6. **Keep images updated** - Regular security updates
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

---

## Additional Resources

- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **Flask Best Practices**: https://flask.palletsprojects.com/
- **PostgreSQL**: https://www.postgresql.org/docs/

---

## Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify environment variables in `.env`
3. Check database connectivity
4. Review this troubleshooting guide
5. Open an issue on GitHub with logs and error messages

---

**Made with ❤️ for church communities**

