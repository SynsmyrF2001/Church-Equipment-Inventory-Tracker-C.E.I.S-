"""
JWT Authentication System with Email and SMS Verification
Provides secure user authentication with two-factor verification
"""

import os
import jwt
import random
import string
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import Client
from app import db
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """Main authentication service handling JWT tokens and verification codes"""
    
    def __init__(self):
        self.jwt_secret = os.environ.get('SESSION_SECRET')
        if not self.jwt_secret:
            raise ValueError("SESSION_SECRET environment variable is required for JWT authentication")
        self.jwt_algorithm = 'HS256'
        self.token_expiry_hours = 24
        self.verification_code_expiry_minutes = 10
        
        # Twilio setup
        self.twilio_client = None
        if all([os.environ.get('TWILIO_ACCOUNT_SID'), 
                os.environ.get('TWILIO_AUTH_TOKEN'),
                os.environ.get('TWILIO_PHONE_NUMBER')]):
            self.twilio_client = Client(
                os.environ.get('TWILIO_ACCOUNT_SID'),
                os.environ.get('TWILIO_AUTH_TOKEN')
            )
            self.twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')
        
    def generate_jwt_token(self, user_id, email):
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token
    
    def verify_jwt_token(self, token):
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
    
    def generate_verification_code(self, length=6):
        """Generate random verification code"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_sms_verification_code(self, phone_number, verification_code):
        """Send SMS verification code using Twilio"""
        if not self.twilio_client:
            logger.error("Twilio client not configured")
            return False
        
        try:
            message = self.twilio_client.messages.create(
                body=f"Your verification code is: {verification_code}. This code expires in {self.verification_code_expiry_minutes} minutes.",
                from_=self.twilio_phone,
                to=phone_number
            )
            logger.info(f"SMS sent successfully with SID: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return False
    
    def send_email_verification_code(self, email, verification_code):
        """Send email verification code (using simple SMTP)"""
        try:
            # For demo purposes - in production, use a proper email service
            msg = MIMEMultipart()
            msg['From'] = "noreply@churchinventory.local"
            msg['To'] = email
            msg['Subject'] = "Email Verification Code"
            
            body = f"""
            Your email verification code is: {verification_code}
            
            This code expires in {self.verification_code_expiry_minutes} minutes.
            
            If you didn't request this code, please ignore this email.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # For development - just log the code instead of sending email
            logger.info(f"Email verification code for {email}: {verification_code}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def hash_password(self, password):
        """Hash password securely"""
        return generate_password_hash(password)
    
    def verify_password(self, password, password_hash):
        """Verify password against hash"""
        return check_password_hash(password_hash, password)

# Global auth service instance
auth_service = AuthService()


def require_jwt_auth(f):
    """Decorator to require JWT authentication"""
    from functools import wraps
    from flask import request, jsonify, g
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid authorization header format'}), 401
        
        if not token:
            return jsonify({'error': 'Authorization token is missing'}), 401
        
        payload = auth_service.verify_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user info to request context
        g.current_user_id = payload['user_id']
        g.current_user_email = payload['email']
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_verification(verification_type='email'):
    """Decorator to require verification (email or phone)"""
    from functools import wraps
    from flask import jsonify, g
    from models import User
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user_id'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user = User.query.get(g.current_user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if verification_type == 'email' and not user.email_verified:
                return jsonify({'error': 'Email verification required'}), 403
            elif verification_type == 'phone' and not user.phone_verified:
                return jsonify({'error': 'Phone verification required'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator