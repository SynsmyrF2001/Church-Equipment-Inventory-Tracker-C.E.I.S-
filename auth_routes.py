"""
Authentication Routes for JWT-based user system
Handles registration, login, verification, and authentication
"""

from flask import Blueprint, request, jsonify, g, render_template
from datetime import datetime, timedelta
import re
from auth import auth_service, require_jwt_auth, require_verification
from models import User, VerificationCode, db
import logging

logger = logging.getLogger(__name__)

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format (basic US format)"""
    pattern = r'^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$'
    # Remove spaces, dashes, parentheses
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    return re.match(pattern, clean_phone) is not None

def format_phone(phone):
    """Format phone number to E.164 format"""
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    if not clean_phone.startswith('+'):
        if clean_phone.startswith('1'):
            clean_phone = '+' + clean_phone
        else:
            clean_phone = '+1' + clean_phone
    return clean_phone

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        phone_number = data.get('phone_number', '').strip()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate phone if provided
        if phone_number and not validate_phone(phone_number):
            return jsonify({'error': 'Invalid phone number format'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Check phone number uniqueness if provided
        if phone_number:
            formatted_phone = format_phone(phone_number)
            existing_phone = User.query.filter_by(phone_number=formatted_phone).first()
            if existing_phone:
                return jsonify({'error': 'User with this phone number already exists'}), 409
        
        # Validate password strength
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # Create new user
        user = User(
            email=email,
            password_hash=auth_service.hash_password(password),
            phone_number=format_phone(phone_number) if phone_number else None,
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip()
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Send email verification code
        email_code = auth_service.generate_verification_code()
        email_verification = VerificationCode(
            user_id=user.id,
            code=email_code,
            code_type='email',
            purpose='registration',
            expires_at=datetime.utcnow() + timedelta(minutes=auth_service.verification_code_expiry_minutes)
        )
        db.session.add(email_verification)
        
        # Send phone verification code if phone provided
        phone_verification = None
        if phone_number:
            phone_code = auth_service.generate_verification_code()
            phone_verification = VerificationCode(
                user_id=user.id,
                code=phone_code,
                code_type='phone',
                purpose='registration',
                expires_at=datetime.utcnow() + timedelta(minutes=auth_service.verification_code_expiry_minutes)
            )
            db.session.add(phone_verification)
            
            # Send SMS
            if not auth_service.send_sms_verification_code(user.phone_number, phone_code):
                logger.warning(f"Failed to send SMS verification to {user.phone_number}")
        
        # Send email (in development, just log it)
        auth_service.send_email_verification_code(user.email, email_code)
        
        db.session.commit()
        
        response_data = {
            'message': 'User registered successfully',
            'user_id': user.id,
            'verification_required': {
                'email': True,
                'phone': phone_number is not None
            }
        }
        
        logger.info(f"New user registered: {user.email}")
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/verify', methods=['POST'])
def verify_code():
    """Verify email or phone verification code"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'code', 'code_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        user_id = data['user_id']
        code = data['code']
        code_type = data['code_type']  # 'email' or 'phone'
        
        if code_type not in ['email', 'phone']:
            return jsonify({'error': 'Invalid code type'}), 400
        
        # Find user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Find valid verification code
        verification = VerificationCode.query.filter_by(
            user_id=user_id,
            code=code,
            code_type=code_type,
            used_at=None
        ).filter(VerificationCode.expires_at > datetime.utcnow()).first()
        
        if not verification:
            return jsonify({'error': 'Invalid or expired verification code'}), 400
        
        # Mark code as used
        verification.used_at = datetime.utcnow()
        
        # Update user verification status
        if code_type == 'email':
            user.email_verified = True
        elif code_type == 'phone':
            user.phone_verified = True
        
        db.session.commit()
        
        logger.info(f"User {user.email} verified {code_type}")
        
        return jsonify({
            'message': f'{code_type.title()} verified successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Verification error: {str(e)}")
        return jsonify({'error': 'Verification failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user or not auth_service.verify_password(password, user.password_hash):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Check if email is verified
        if not user.email_verified:
            return jsonify({
                'error': 'Email verification required',
                'user_id': user.id,
                'verification_required': 'email'
            }), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate JWT token
        token = auth_service.generate_jwt_token(user.id, user.email)
        
        logger.info(f"User logged in: {user.email}")
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification code"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'code_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        user_id = data['user_id']
        code_type = data['code_type']  # 'email' or 'phone'
        
        if code_type not in ['email', 'phone']:
            return jsonify({'error': 'Invalid code type'}), 400
        
        # Find user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if already verified
        if code_type == 'email' and user.email_verified:
            return jsonify({'error': 'Email already verified'}), 400
        elif code_type == 'phone' and user.phone_verified:
            return jsonify({'error': 'Phone already verified'}), 400
        
        # Invalidate existing codes
        existing_codes = VerificationCode.query.filter_by(
            user_id=user_id,
            code_type=code_type,
            used_at=None
        ).all()
        
        for code in existing_codes:
            code.used_at = datetime.utcnow()
        
        # Generate new code
        new_code = auth_service.generate_verification_code()
        verification = VerificationCode(
            user_id=user_id,
            code=new_code,
            code_type=code_type,
            purpose='registration',
            expires_at=datetime.utcnow() + timedelta(minutes=auth_service.verification_code_expiry_minutes)
        )
        db.session.add(verification)
        
        # Send code
        if code_type == 'email':
            auth_service.send_email_verification_code(user.email, new_code)
        elif code_type == 'phone':
            if not user.phone_number:
                return jsonify({'error': 'No phone number on file'}), 400
            if not auth_service.send_sms_verification_code(user.phone_number, new_code):
                return jsonify({'error': 'Failed to send SMS'}), 500
        
        db.session.commit()
        
        return jsonify({'message': f'Verification code sent to {code_type}'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Resend verification error: {str(e)}")
        return jsonify({'error': 'Failed to resend verification code'}), 500

@auth_bp.route('/profile', methods=['GET'])
@require_jwt_auth
def get_profile():
    """Get current user profile"""
    try:
        user = User.query.get(g.current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return jsonify({'error': 'Failed to get profile'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@require_jwt_auth
@require_verification('email')
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        user = User.query.get(g.current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name'].strip()
        if 'last_name' in data:
            user.last_name = data['last_name'].strip()
        
        # Handle phone number update
        if 'phone_number' in data:
            phone_number = data['phone_number'].strip()
            if phone_number:
                if not validate_phone(phone_number):
                    return jsonify({'error': 'Invalid phone number format'}), 400
                
                formatted_phone = format_phone(phone_number)
                
                # Check if phone is already taken by another user
                existing_phone = User.query.filter(
                    User.phone_number == formatted_phone,
                    User.id != user.id
                ).first()
                
                if existing_phone:
                    return jsonify({'error': 'Phone number already in use'}), 409
                
                # If phone number changed, mark as unverified
                if user.phone_number != formatted_phone:
                    user.phone_number = formatted_phone
                    user.phone_verified = False
            else:
                user.phone_number = None
                user.phone_verified = False
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Profile update error: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500

@auth_bp.route('/logout', methods=['POST'])
@require_jwt_auth
def logout():
    """Logout user (client should discard JWT token)"""
    # With JWT, logout is handled client-side by discarding the token
    # In a production system, you might want to maintain a blacklist of tokens
    logger.info(f"User logged out: {g.current_user_email}")
    return jsonify({'message': 'Logged out successfully'}), 200

# Error handlers
@auth_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@auth_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401

@auth_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden'}), 403

@auth_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@auth_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# HTML Page Routes for Authentication
@auth_bp.route('/register-page')
def register_page():
    """Registration page"""
    return render_template('auth/register.html')

@auth_bp.route('/login-page')  
def login_page():
    """Login page"""
    return render_template('auth/login.html')

@auth_bp.route('/verify-page')
def verify_page():
    """Verification page"""
    return render_template('auth/verify.html')