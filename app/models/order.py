from app.models import db
from datetime import datetime


class Order(db.Model):
    """Customer order model."""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_ref = db.Column(db.String(20), unique=True, nullable=False)
    customer_name = db.Column(db.String(150), default='Walk-in')
    status = db.Column(db.String(20), default='received')  # received, preparing, ready, completed, cancelled
    total_amount = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text, default='')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    @staticmethod
    def generate_ref():
        """Generate a unique order reference."""
        import random
        import string
        now = datetime.utcnow()
        date_str = now.strftime('%m%d')
        rand = ''.join(random.choices(string.digits, k=4))
        return f'ORD-{date_str}-{rand}'

    def calculate_total(self):
        self.total_amount = sum(item.subtotal for item in self.items)

    def to_dict(self):
        return {
            'id': self.id,
            'order_ref': self.order_ref,
            'customer_name': self.customer_name,
            'status': self.status,
            'total_amount': self.total_amount,
            'notes': self.notes,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class OrderItem(db.Model):
    """Individual line item in an order."""
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    special_instructions = db.Column(db.Text, default='')

    menu_item = db.relationship('MenuItem')

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    def to_dict(self):
        return {
            'id': self.id,
            'menu_item_id': self.menu_item_id,
            'menu_item_name': self.menu_item.name_en if self.menu_item else '',
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'subtotal': self.subtotal,
            'special_instructions': self.special_instructions
        }
