from app.models import db
from datetime import datetime


class Booking(db.Model):
    """Seat/slot booking model."""
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    booking_ref = db.Column(db.String(20), unique=True, nullable=False)  # e.g., NOD-20260620-001
    customer_name = db.Column(db.String(150), nullable=False)
    customer_email = db.Column(db.String(120), default='')
    customer_phone = db.Column(db.String(20), default='')
    date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)  # e.g., "10:00-11:00"
    guest_count = db.Column(db.Integer, default=1)
    seating_preference = db.Column(db.String(20), default='any')  # indoor, outdoor, any
    status = db.Column(db.String(20), default='confirmed')  # pending, confirmed, cancelled, completed, no_show
    notes = db.Column(db.Text, default='')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def generate_ref(date):
        """Generate a unique booking reference."""
        import random
        import string
        date_str = date.strftime('%Y%m%d')
        rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f'NOD-{date_str}-{rand}'

    def to_dict(self):
        return {
            'id': self.id,
            'booking_ref': self.booking_ref,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'date': self.date.isoformat() if self.date else None,
            'time_slot': self.time_slot,
            'guest_count': self.guest_count,
            'seating_preference': self.seating_preference,
            'status': self.status,
            'notes': self.notes,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
