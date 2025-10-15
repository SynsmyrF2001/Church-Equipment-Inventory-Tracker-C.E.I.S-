# 🔒 Security Guide

This document outlines security best practices for the Church Equipment Inventory System.

## 🚨 **CRITICAL: SMTP Credential Leak Fixed**

**Issue Resolved:** Hardcoded JWT secret and default passwords have been removed from the codebase.

### What Was Fixed:
- ✅ Removed hardcoded JWT secret from `auth.py`
- ✅ Updated default passwords to require explicit configuration
- ✅ Enhanced `.gitignore` to prevent future credential leaks
- ✅ Added security validation for required environment variables

---

## 🔐 Security Best Practices

### 1. Environment Variables

**NEVER commit these files:**
- `.env`
- `.env.local`
- `.env.production`
- `secrets/`
- `credentials/`

**Required Environment Variables:**
```bash
# Security (REQUIRED)
SESSION_SECRET=<generate-strong-64-char-secret>

# Database (REQUIRED)
POSTGRES_PASSWORD=<strong-database-password>
DATABASE_URL=postgresql://user:password@host:port/database

# Optional Services
TWILIO_ACCOUNT_SID=<your-twilio-sid>
TWILIO_AUTH_TOKEN=<your-twilio-token>
MAIL_PASSWORD=<your-email-password>
```

### 2. Generate Secure Secrets

**Session Secret:**
```bash
# Generate a secure 64-character secret
python3 -c 'import secrets; print(secrets.token_hex(32))'

# Or using OpenSSL
openssl rand -hex 32
```

**Database Password:**
```bash
# Generate a strong password
openssl rand -base64 32
```

### 3. Production Security Checklist

- [ ] **Change all default passwords**
- [ ] **Use strong, unique passwords (20+ characters)**
- [ ] **Enable HTTPS/SSL in production**
- [ ] **Use environment variables for all secrets**
- [ ] **Regular security updates**
- [ ] **Database backups are encrypted**
- [ ] **Access logs are monitored**
- [ ] **Firewall rules are configured**

---

## 🛡️ Security Features

### Authentication & Authorization
- ✅ **JWT-based authentication** with secure token generation
- ✅ **Password hashing** using Werkzeug's secure methods
- ✅ **Email verification** for account activation
- ✅ **Phone verification** via Twilio (optional)
- ✅ **Session management** with secure cookies

### Data Protection
- ✅ **SQL injection protection** via SQLAlchemy ORM
- ✅ **Input validation** on all forms
- ✅ **CSRF protection** via Flask-WTF
- ✅ **Secure headers** in production (via Nginx)

### Container Security
- ✅ **Non-root user** in Docker containers
- ✅ **Minimal base images** (Alpine Linux)
- ✅ **No hardcoded secrets** in images
- ✅ **Health checks** for monitoring

---

## 🚨 Security Incident Response

### If You Suspect a Breach:

1. **Immediately rotate all secrets:**
   ```bash
   # Generate new session secret
   python3 -c 'import secrets; print(secrets.token_hex(32))'
   
   # Change database password
   # Update all environment variables
   ```

2. **Check for unauthorized access:**
   ```bash
   # Review application logs
   docker-compose logs web
   
   # Check database access logs
   docker-compose logs db
   ```

3. **Update all credentials:**
   - Database passwords
   - API keys (Twilio, email services)
   - Session secrets
   - OAuth credentials

4. **Deploy security updates:**
   ```bash
   # Rebuild containers with new secrets
   docker-compose down
   docker-compose up --build
   ```

---

## 🔍 Security Monitoring

### Health Checks
The application includes health check endpoints:
- **Application Health:** `GET /health`
- **Database Health:** Built into application health check

### Log Monitoring
Monitor these logs for security events:
```bash
# Application logs
docker-compose logs -f web

# Database logs
docker-compose logs -f db

# System logs
docker system events
```

### Suspicious Activity Indicators
- Multiple failed login attempts
- Unusual database queries
- High memory/CPU usage
- Network connection anomalies

---

## 🛠️ Security Tools

### Pre-commit Security Checks
```bash
# Install security scanning tools
pip install bandit safety

# Run security scans
bandit -r . -f json -o security-report.json
safety check
```

### Docker Security Scanning
```bash
# Scan Docker images for vulnerabilities
docker scout cves churchinventorytracker-web:latest
```

### Git Security
```bash
# Install GitGuardian CLI
pip install ggshield

# Scan for secrets
ggshield scan path .
```

---

## 📋 Security Checklist

### Before Deployment:
- [ ] All secrets are in environment variables
- [ ] No hardcoded credentials in code
- [ ] Strong passwords are used
- [ ] HTTPS is enabled
- [ ] Database is secured
- [ ] Logs are configured
- [ ] Backup strategy is in place

### Regular Maintenance:
- [ ] Update dependencies monthly
- [ ] Rotate secrets quarterly
- [ ] Review access logs weekly
- [ ] Test backup/restore procedures
- [ ] Security scan before releases

---

## 🆘 Emergency Contacts

### Security Issues:
1. **Immediate:** Rotate all secrets
2. **Document:** Record incident details
3. **Notify:** Alert stakeholders if needed
4. **Investigate:** Review logs and access patterns
5. **Remediate:** Fix vulnerabilities and update security

### Quick Commands:
```bash
# Emergency secret rotation
docker-compose down
# Update .env with new secrets
docker-compose up -d

# Check for running processes
docker-compose ps

# View recent logs
docker-compose logs --tail=100
```

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)

---

**Remember: Security is an ongoing process, not a one-time setup!**

---

*Last Updated: October 9, 2025*  
*Version: 1.0*

---

**Made with ❤️ for secure church communities**
