from app.models import db
from datetime import datetime
import json


class MenuCategory(db.Model):
    """Menu category (e.g., Coffee, Tea, Snacks)."""
    __tablename__ = 'menu_categories'

    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(100), nullable=False)
    name_hi = db.Column(db.String(100), nullable=False, default='')
    icon = db.Column(db.String(10), default='☕')  # Emoji icon
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('MenuItem', backref='category', lazy=True, order_by='MenuItem.display_order')

    def to_dict(self, lang='en'):
        return {
            'id': self.id,
            'name': self.name_hi if lang == 'hi' and self.name_hi else self.name_en,
            'name_en': self.name_en,
            'name_hi': self.name_hi,
            'icon': self.icon,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'item_count': len([i for i in self.items if i.is_available])
        }


class MenuItem(db.Model):
    """Individual menu item."""
    __tablename__ = 'menu_items'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('menu_categories.id'), nullable=False)
    name_en = db.Column(db.String(150), nullable=False)
    name_hi = db.Column(db.String(150), nullable=False, default='')
    description_en = db.Column(db.Text, default='')
    description_hi = db.Column(db.Text, default='')
    price = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(300), default='')
    tags = db.Column(db.Text, default='[]')  # JSON array: ["Bestseller", "Vegan", "New", "Spicy"]
    is_available = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_tags(self):
        try:
            return json.loads(self.tags) if self.tags else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_tags(self, tags_list):
        self.tags = json.dumps(tags_list)

    def to_dict(self, lang='en'):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'name': self.name_hi if lang == 'hi' and self.name_hi else self.name_en,
            'name_en': self.name_en,
            'name_hi': self.name_hi,
            'description': self.description_hi if lang == 'hi' and self.description_hi else self.description_en,
            'description_en': self.description_en,
            'description_hi': self.description_hi,
            'price': self.price,
            'image_path': self.image_path,
            'tags': self.get_tags(),
            'is_available': self.is_available,
            'category_name': self.category.name_hi if lang == 'hi' and self.category.name_hi else self.category.name_en if self.category else ''
        }
