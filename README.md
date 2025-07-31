# Church Equipment Inventory System

A comprehensive Flask-based web application designed to manage and track church technical equipment inventory. Built with simplicity and usability in mind for church staff and volunteers.

![Church Inventory System](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.1+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

### Core Functionality
- **Equipment Management**: Add, edit, and track church equipment with detailed information
- **Check-in/Check-out System**: Complete workflow for equipment borrowing and returns
- **Usage Tracking**: Comprehensive audit trail of all equipment transactions
- **Reporting**: Generate usage statistics and overdue item alerts
- **QR Code Integration**: Generate and scan QR codes for quick equipment identification

### User Experience
- **Multi-language Support**: English, French, and Haitian Creole
- **Interactive Tutorial**: 7-step walkthrough for new users and volunteers
- **Responsive Design**: Mobile-first approach with Bootstrap 5
- **Smart Assistance**: Auto-suggestions, tooltips, and contextual help
- **Keyboard Shortcuts**: Quick access to common functions

### Technical Features
- **Database Support**: SQLite (default) with PostgreSQL compatibility
- **Authentication System**: Secure user management with OAuth support
- **Form Validation**: Comprehensive input validation and error handling
- **Export Capabilities**: CSV export for equipment and history data
- **Dark Theme**: Modern UI with dark mode support

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- pip or uv package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/church-inventory-tracker.git
   cd church-inventory-tracker
   ```

2. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export SESSION_SECRET="your-secret-key-here"
   export DATABASE_URL="sqlite:///church_inventory.db"  # Optional, defaults to SQLite
   ```

4. **Initialize the database**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 📁 Project Structure

```
ChurchInventoryTracker/
├── app.py                 # Main Flask application
├── models.py             # Database models (Equipment, CheckoutHistory)
├── forms.py              # Form definitions and validation
├── routes.py             # Main application routes
├── auth.py               # Authentication utilities
├── auth_routes.py        # Authentication routes
├── qr_utils.py           # QR code generation and scanning
├── static/               # Static assets (CSS, JS, images)
├── templates/            # HTML templates
├── instance/             # Database files (not in git)
└── pyproject.toml        # Project dependencies
```

## 🛠️ Configuration

### Environment Variables
- `SESSION_SECRET`: Required for session security
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `DEBUG`: Enable debug mode (default: False)

### Database Configuration
The system supports multiple database backends:
- **SQLite** (default): Perfect for small to medium churches
- **PostgreSQL**: Recommended for larger deployments
- **MySQL**: Also supported via SQLAlchemy

## 📊 Features in Detail

### Equipment Categories
- Audio equipment (microphones, speakers, mixers)
- Video equipment (cameras, projectors, screens)
- Lighting equipment (lights, stands, controllers)
- Musical instruments
- Cables and connectors
- Computers and tablets
- Other miscellaneous equipment

### Status Tracking
- **Available**: Equipment ready for checkout
- **In Use**: Currently checked out
- **Maintenance**: Under repair or maintenance

### Reporting Features
- Equipment usage statistics
- Overdue item alerts
- Checkout history reports
- Equipment condition tracking
- Export functionality (CSV format)

## 🌍 Internationalization

The application supports multiple languages:
- **English**: Primary language
- **French**: Complete translation
- **Haitian Creole**: Complete translation

Language switching is available through the navigation menu and persists across sessions.

## 🎓 Tutorial System

New users can access an interactive 7-step tutorial that covers:
1. Dashboard overview
2. Adding new equipment
3. Checking out equipment
4. Checking in equipment
5. Searching and filtering
6. Generating reports
7. Using QR codes

## 🔧 Development

### Running in Development Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### Database Migrations
The application uses SQLAlchemy's `create_all()` method for database initialization. For production deployments, consider using Flask-Migrate for proper database migrations.

### Testing
```bash
# Run tests (when implemented)
python -m pytest tests/
```

## 🚀 Deployment

### Production Deployment
1. Set up a production database (PostgreSQL recommended)
2. Configure environment variables
3. Use a WSGI server like Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```



## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- UI powered by [Bootstrap 5](https://getbootstrap.com/)
- Icons from [Feather Icons](https://feathericons.com/)
- QR code generation with [qrcode](https://github.com/lincolnloop/python-qrcode)

## 📞 Support

If you have any questions or need help setting up the system, please:
1. Check the [documentation](overview.md)
2. Open an issue on GitHub
3. Contact the development team

---

**Made with ❤️ for church communities** 