# 📁 Project Structure Guide

This document explains the organized structure of the Church Equipment Inventory System project.

## 🗂️ Directory Organization

### 📁 **Root Directory**
```
ChurchInventoryTracker/
├── 🐍 Core Application Files
│   ├── app.py              # Main Flask application
│   ├── models.py           # Database models (Equipment, User, etc.)
│   ├── routes.py           # Main application routes
│   ├── auth.py             # Authentication system
│   ├── auth_routes.py      # Authentication routes
│   ├── forms.py            # Form definitions and validation
│   ├── qr_utils.py         # QR code generation and scanning
│   └── main.py             # Application entry point
│
├── 📄 Configuration Files
│   ├── requirements.txt    # Python dependencies
│   ├── pyproject.toml      # Project configuration
│   ├── setup.py           # Package setup
│   ├── .gitignore         # Git ignore patterns
│   ├── .dockerignore      # Docker ignore patterns
│   └── LICENSE            # MIT License
│
├── 📁 Static & Templates
│   ├── static/            # CSS, JavaScript, images
│   └── templates/         # HTML templates
│
├── 📁 Data & Runtime
│   └── instance/          # Database files (not in git)
│
└── 📁 Organized Folders
    ├── docs/              # All documentation
    ├── docker/            # Docker configuration
    ├── scripts/           # Utility scripts
    └── config/            # Configuration templates
```

---

## 📚 **docs/** - Documentation

All documentation is centralized in the `docs/` folder:

```
docs/
├── README.md                    # Main project documentation
├── DOCKER.md                    # Complete Docker deployment guide
├── DOCKER_QUICKSTART.md         # 3-minute Docker setup guide
├── SECURITY.md                  # Security best practices
├── SECURITY_FIX_SUMMARY.md      # Security fixes documentation
├── CONTRIBUTING.md              # Contribution guidelines
├── DEPLOYMENT.md                # Production deployment guide
├── PROJECT_STRUCTURE.md         # This file
└── overview.md                  # Project overview
```

**Purpose:** Keep all documentation organized and easy to find.

---

## 🐳 **docker/** - Docker Configuration

All Docker-related files are in the `docker/` folder:

```
docker/
├── Dockerfile                   # Multi-stage Docker build
├── docker-compose.yml          # Container orchestration
└── nginx/                      # Nginx configuration
    └── nginx.conf              # Production reverse proxy config
```

**Purpose:** Isolate Docker configuration for cleaner project structure.

**Usage:**
```bash
# Run Docker from project root
docker-compose -f docker/docker-compose.yml up

# Or use the script
./scripts/docker-start.sh
```

---

## 🔧 **scripts/** - Utility Scripts

All executable scripts are in the `scripts/` folder:

```
scripts/
├── docker-start.sh              # One-command Docker setup
├── quick_start.sh               # Traditional Python setup
├── entrypoint.sh                # Container initialization script
└── GIT_COMMIT_COMMANDS.sh       # Git helper script
```

**Purpose:** Keep all scripts organized and easily accessible.

**Usage:**
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run Docker setup
./scripts/docker-start.sh

# Run traditional setup
./scripts/quick_start.sh
```

---

## ⚙️ **config/** - Configuration Templates

Configuration templates and examples:

```
config/
└── env.example                  # Environment variables template
```

**Purpose:** Provide configuration templates without cluttering the root directory.

**Usage:**
```bash
# Copy template to create your environment file
cp config/env.example .env

# Edit with your values
nano .env
```

---

## 🎯 **Benefits of This Structure**

### ✅ **Cleaner Root Directory**
- Only essential files in root
- Easy to find core application files
- Reduced clutter and confusion

### ✅ **Logical Organization**
- Related files grouped together
- Clear separation of concerns
- Easy to navigate for new developers

### ✅ **Scalability**
- Easy to add new documentation
- Simple to add new scripts
- Clear structure for future features

### ✅ **Maintenance**
- Easy to find and update files
- Clear ownership of different components
- Simplified deployment processes

---

## 🚀 **Quick Navigation**

### **For Developers:**
- **Core Code:** `app.py`, `models.py`, `routes.py`, `auth.py`
- **Templates:** `templates/`
- **Static Files:** `static/`
- **Configuration:** `config/env.example`

### **For DevOps:**
- **Docker:** `docker/` folder
- **Scripts:** `scripts/` folder
- **Documentation:** `docs/` folder

### **For Users:**
- **Setup:** `docs/DOCKER_QUICKSTART.md`
- **Documentation:** `docs/README.md`
- **Security:** `docs/SECURITY.md`

---

## 📋 **File Naming Conventions**

### **Documentation:**
- `README.md` - Main documentation
- `DOCKER.md` - Docker-specific docs
- `SECURITY.md` - Security documentation
- `CONTRIBUTING.md` - Contribution guidelines

### **Scripts:**
- `*-start.sh` - Setup/startup scripts
- `entrypoint.sh` - Container entry points
- `quick_*.sh` - Quick setup scripts

### **Configuration:**
- `*.example` - Configuration templates
- `docker-compose.yml` - Container orchestration
- `Dockerfile` - Container build instructions

---

## 🔄 **Migration Notes**

### **What Changed:**
- Moved all `.md` files to `docs/`
- Moved Docker files to `docker/`
- Moved scripts to `scripts/`
- Moved config templates to `config/`

### **Updated References:**
- Docker compose now uses `docker/docker-compose.yml`
- Scripts now in `scripts/` folder
- Documentation now in `docs/` folder

### **Backward Compatibility:**
- All functionality preserved
- Scripts updated to work with new structure
- Docker configuration updated
- Documentation links updated

---

## 🎉 **Result**

Your project is now:
- ✅ **Organized** - Clear folder structure
- ✅ **Professional** - Industry-standard organization
- ✅ **Maintainable** - Easy to find and update files
- ✅ **Scalable** - Ready for future growth
- ✅ **Clean** - No clutter in root directory

---

**Made with ❤️ for organized church communities**

---

*Last Updated: October 15, 2025*  
*Structure Version: 2.0*
