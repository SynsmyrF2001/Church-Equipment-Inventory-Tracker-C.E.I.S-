# Church Equipment Inventory System

## Overview

This is a Flask-based web application designed to manage and track church technical equipment inventory. The system provides comprehensive equipment management with check-in/check-out functionality, usage tracking, and reporting capabilities. Built with a focus on simplicity and usability for church staff and volunteers.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLite (default) with SQLAlchemy ORM support
- **Database URL**: Configurable via environment variables, supports external databases
- **Forms**: Flask-WTF for form handling and validation
- **Session Management**: Flask sessions with configurable secret key

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5 with dark theme support
- **Icons**: Feather Icons for consistent iconography
- **JavaScript**: Vanilla JavaScript for enhanced interactivity
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Database Schema
- **Equipment Table**: Core inventory items with status tracking
- **CheckoutHistory Table**: Complete audit trail of equipment usage
- **Relationships**: One-to-many between Equipment and CheckoutHistory

## Key Components

### Models (models.py)
- **Equipment Model**: Stores equipment details, status, and metadata
  - Supports categories: audio, video, lighting, instruments, cables, computers, other
  - Status tracking: available, in-use, maintenance
  - Purchase information and location tracking
- **CheckoutHistory Model**: Tracks all check-in/check-out transactions
  - Includes condition assessment and notes
  - Supports overdue item detection

### Forms (forms.py)
- **EquipmentForm**: Add/edit equipment with comprehensive validation
- **CheckoutForm**: Equipment checkout with expected return dates
- **CheckinForm**: Equipment return with condition assessment
- **SearchForm**: Dashboard search and filtering capabilities

### Routes (routes.py)
- Dashboard with statistics and search functionality
- CRUD operations for equipment management
- Check-in/check-out workflow
- Reporting and data export capabilities
- CSV export for equipment and history data

## Data Flow

1. **Equipment Registration**: Staff adds new equipment through EquipmentForm
2. **Equipment Checkout**: Users check out equipment via CheckoutForm, status changes to 'in-use'
3. **Equipment Checkin**: Users return equipment via CheckinForm, status returns to 'available'
4. **History Tracking**: All transactions recorded in CheckoutHistory for audit trail
5. **Reporting**: System generates usage statistics and overdue item alerts

## External Dependencies

### Python Packages
- Flask: Web framework
- Flask-SQLAlchemy: Database ORM
- Flask-WTF: Form handling
- WTForms: Form validation
- Werkzeug: WSGI utilities

### Frontend Dependencies
- Bootstrap 5: UI framework (CDN)
- Feather Icons: Icon library (CDN)
- Custom CSS for branding and enhancements

### Infrastructure
- ProxyFix middleware for reverse proxy support
- Environment variable configuration for deployment flexibility

## Deployment Strategy

### Environment Configuration
- `SESSION_SECRET`: Required for session security
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- Debug logging enabled for development

### Production Considerations
- SQLAlchemy connection pooling configured
- WSGI-compatible for various deployment platforms
- Database migrations handled via create_all() method
- Static file serving through Flask (suitable for small deployments)

### Scalability Notes
- Database engine supports connection pooling and pre-ping
- Application structured for easy migration to PostgreSQL or other databases
- Modular design allows for easy feature extensions

## Recent Updates

### July 01, 2025 - Language Support & Tutorial System
- **Multi-language Support**: Added language switching for English, French, and Haitian Creole
- **Interactive Tutorial**: 7-step walkthrough system for training newcomers and volunteers
- **Novice-Friendly Enhancements**: Smart form assistance, helpful tooltips, and contextual help
- **Visual Improvements**: Enhanced animations, hover effects, and interactive feedback
- **Keyboard Shortcuts**: Added Ctrl+H for help, Ctrl+N for new equipment, Esc to clear search
- **Auto-suggestions**: Equipment name and location suggestions for faster data entry

### Architecture Changes
- **Flask-Babel Integration**: Added internationalization support with locale detection
- **Session Management**: Enhanced session handling for language preferences and tutorial completion
- **Enhanced JavaScript**: Added comprehensive novice assistance features and tutorial navigation
- **CSS Animations**: Added interactive elements with smooth transitions and visual feedback

## Key Components

### Language System
- **Babel Configuration**: Supports English, French, and Haitian Creole with automatic detection
- **Language Switcher**: Dropdown menu in navigation for instant language switching
- **Session Persistence**: Language preference saved across sessions

### Tutorial System
- **7-Step Interactive Guide**: Comprehensive walkthrough covering all major features
- **Progress Tracking**: Visual progress indicators and step navigation
- **Contextual Help**: Smart assistance based on user actions and current page
- **Keyboard Navigation**: Arrow keys for step navigation, shortcuts for common actions

### Novice-Friendly Features
- **Smart Tooltips**: Automatic help text for all interactive elements
- **Form Assistance**: Equipment name suggestions and location auto-complete
- **Visual Feedback**: Button animations, hover effects, and status explanations
- **Contextual Hints**: Helpful information displayed based on user context

## User Preferences

Preferred communication style: Simple, everyday language.
Target users: Church volunteers and staff with varying technical experience.
Priority features: Ease of use, clear guidance, multi-language support.