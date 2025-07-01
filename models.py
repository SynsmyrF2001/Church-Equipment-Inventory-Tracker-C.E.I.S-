from datetime import datetime
from app import db


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
        return f'<CheckoutHistory {self.equipment.name} - {self.checked_out_by}>'
    
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
