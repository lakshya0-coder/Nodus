import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from app.models.menu import MenuItem
from seed_data import items_data

def update_images():
    app = create_app()
    with app.app_context():
        for item_data in items_data:
            item = MenuItem.query.filter_by(name_en=item_data['name_en']).first()
            if item:
                item.image_path = item_data.get('image_path', '')
                print(f"Updated {item.name_en} -> {item.image_path}")
        db.session.commit()
        print("Done!")

if __name__ == '__main__':
    update_images()
