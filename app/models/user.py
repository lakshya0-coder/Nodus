from app.models import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
    """User model for customers, staff, admins, and developers."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(150), default='')
    phone = db.Column(db.String(20), default='')
    role = db.Column(db.String(20), default='customer')  # customer, staff, admin, developer
    preferred_language = db.Column(db.String(5), default='en')  # en, hi
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    conversations = db.relationship('Conversation', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role in ('admin', 'developer')

    @property
    def is_staff(self):
        return self.role in ('staff', 'admin', 'developer')

    @property
    def is_developer(self):
        return self.role == 'developer'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'preferred_language': self.preferred_language,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class StaffRole(db.Model):
    """Extended role/permission mapping for staff."""
    __tablename__ = 'staff_roles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permission = db.Column(db.String(50), nullable=False)  # e.g., 'manage_orders', 'manage_bookings', etc.
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='staff_permissions')
