from datetime import datetime
from app import db
import secrets


class Equipment(db.Model):
    """Model for technical equipment inventory items"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='available')  # available, in-use, maintenance
    location = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    purchase_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with checkout history
    checkout_history = db.relationship('CheckoutHistory', backref='equipment', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Equipment {self.name}>'
    
    @property
    def current_checkout(self):
        """Get the current active checkout if equipment is in use"""
        return CheckoutHistory.query.filter_by(
            equipment_id=self.id,
            checked_in_at=None
        ).first()


class CheckoutHistory(db.Model):
    """Model for tracking equipment check-in/check-out history"""
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    checked_out_by = db.Column(db.String(100), nullable=False)
    checked_out_at = db.Column(db.DateTime, default=datetime.utcnow)
    expected_return_date = db.Column(db.Date)
    checked_in_at = db.Column(db.DateTime)
    checked_in_by = db.Column(db.String(100))
    notes = db.Column(db.Text)
    condition_out = db.Column(db.String(20), default='good')  # good, fair, poor
    condition_in = db.Column(db.String(20))
    
    def __repr__(self):
        return f'<CheckoutHistory {self.checked_out_by}>'
    
    @property
    def is_overdue(self):
        """Check if the checkout is overdue"""
        if self.checked_in_at or not self.expected_return_date:
            return False
        return datetime.now().date() > self.expected_return_date
    
    @property
    def duration_days(self):
        """Calculate duration of checkout in days"""
        if self.checked_in_at:
            return (self.checked_in_at - self.checked_out_at).days
        else:
            return (datetime.utcnow() - self.checked_out_at).days


class User(db.Model):
    """User model for authentication system"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=True, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    # Verification status
    email_verified = db.Column(db.Boolean, default=False)
    phone_verified = db.Column(db.Boolean, default=False)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    verification_codes = db.relationship('VerificationCode', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """Convert user to dictionary for JSON responses"""
        return {
            'id': self.id,
            'email': self.email,
            'phone_number': self.phone_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email_verified': self.email_verified,
            'phone_verified': self.phone_verified,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class VerificationCode(db.Model):
    """Model for storing verification codes"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    code_type = db.Column(db.String(20), nullable=False)  # 'email' or 'phone'
    purpose = db.Column(db.String(30), nullable=False)    # 'registration', 'login', 'password_reset'
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<VerificationCode {self.code}>'
    
    @property
    def is_expired(self):
        """Check if verification code has expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_used(self):
        """Check if verification code has been used"""
        return self.used_at is not None
    
    @property
    def is_valid(self):
        """Check if verification code is valid (not expired and not used)"""
        return not self.is_expired and not self.is_used
