"""Menu Management API endpoints."""
import os
import json
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.routes.auth import staff_required
from app.models import db
from app.models.menu import MenuCategory, MenuItem

api_menu_bp = Blueprint('api_menu', __name__)


@api_menu_bp.route('/categories', methods=['GET'])
def list_categories():
    """List all menu categories."""
    lang = request.args.get('lang', 'en')
    categories = MenuCategory.query.order_by(MenuCategory.display_order).all()
    return jsonify({
        'categories': [c.to_dict(lang) for c in categories]
    })


@api_menu_bp.route('/categories', methods=['POST'])
@staff_required
def create_category():
    """Create a menu category."""
    data = request.get_json()
    if not data or not data.get('name_en'):
        return jsonify({'error': 'name_en is required'}), 400

    category = MenuCategory(
        name_en=data['name_en'],
        name_hi=data.get('name_hi', ''),
        icon=data.get('icon', '☕'),
        display_order=data.get('display_order', 0),
        is_active=data.get('is_active', True)
    )
    db.session.add(category)
    db.session.commit()

    return jsonify({'success': True, 'category': category.to_dict()}), 201


@api_menu_bp.route('/categories/<int:cat_id>', methods=['PATCH'])
@staff_required
def update_category(cat_id):
    """Update a menu category."""
    category = MenuCategory.query.get_or_404(cat_id)
    data = request.get_json()

    if 'name_en' in data:
        category.name_en = data['name_en']
    if 'name_hi' in data:
        category.name_hi = data['name_hi']
    if 'icon' in data:
        category.icon = data['icon']
    if 'display_order' in data:
        category.display_order = data['display_order']
    if 'is_active' in data:
        category.is_active = data['is_active']

    db.session.commit()
    return jsonify({'success': True, 'category': category.to_dict()})


@api_menu_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
@staff_required
def delete_category(cat_id):
    """Delete a menu category."""
    category = MenuCategory.query.get_or_404(cat_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Category deleted'})


@api_menu_bp.route('/items', methods=['GET'])
def list_items():
    """List all menu items."""
    lang = request.args.get('lang', 'en')
    category_id = request.args.get('category_id', type=int)
    available_only = request.args.get('available_only', 'false').lower() == 'true'

    query = MenuItem.query.order_by(MenuItem.display_order)

    if category_id:
        query = query.filter_by(category_id=category_id)
    if available_only:
        query = query.filter_by(is_available=True)

    items = query.all()
    return jsonify({
        'items': [i.to_dict(lang) for i in items]
    })


@api_menu_bp.route('/items', methods=['POST'])
@staff_required
def create_item():
    """Create a menu item."""
    # Handle both JSON and form data (for file uploads)
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form.to_dict()
        if 'tags' in data:
            try:
                data['tags'] = json.loads(data['tags'])
            except (json.JSONDecodeError, TypeError):
                data['tags'] = []
    else:
        data = request.get_json() or {}

    if not data.get('name_en') or not data.get('category_id') or not data.get('price'):
        return jsonify({'error': 'name_en, category_id, and price are required'}), 400

    item = MenuItem(
        category_id=int(data['category_id']),
        name_en=data['name_en'],
        name_hi=data.get('name_hi', ''),
        description_en=data.get('description_en', ''),
        description_hi=data.get('description_hi', ''),
        price=float(data['price']),
        is_available=data.get('is_available', True) in (True, 'true', '1', 'True'),
        display_order=int(data.get('display_order', 0))
    )

    if isinstance(data.get('tags'), list):
        item.set_tags(data['tags'])

    # Handle image upload
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            filename = f"menu_{item.name_en.lower().replace(' ', '_')}_{os.urandom(4).hex()}.jpg"
            upload_dir = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            item.image_path = f"/static/images/uploads/{filename}"

    if data.get('image_path'):
        item.image_path = data['image_path']

    db.session.add(item)
    db.session.commit()

    return jsonify({'success': True, 'item': item.to_dict()}), 201


@api_menu_bp.route('/items/<int:item_id>', methods=['PATCH'])
@staff_required
def update_item(item_id):
    """Update a menu item."""
    item = MenuItem.query.get_or_404(item_id)

    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form.to_dict()
        if 'tags' in data:
            try:
                data['tags'] = json.loads(data['tags'])
            except (json.JSONDecodeError, TypeError):
                data['tags'] = []
    else:
        data = request.get_json() or {}

    if 'name_en' in data:
        item.name_en = data['name_en']
    if 'name_hi' in data:
        item.name_hi = data['name_hi']
    if 'description_en' in data:
        item.description_en = data['description_en']
    if 'description_hi' in data:
        item.description_hi = data['description_hi']
    if 'price' in data:
        item.price = float(data['price'])
    if 'category_id' in data:
        item.category_id = int(data['category_id'])
    if 'is_available' in data:
        item.is_available = data['is_available'] in (True, 'true', '1', 'True')
    if 'display_order' in data:
        item.display_order = int(data['display_order'])
    if isinstance(data.get('tags'), list):
        item.set_tags(data['tags'])
    if data.get('image_path'):
        item.image_path = data['image_path']

    # Handle image upload
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            filename = f"menu_{item.name_en.lower().replace(' ', '_')}_{os.urandom(4).hex()}.jpg"
            upload_dir = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            item.image_path = f"/static/images/uploads/{filename}"

    db.session.commit()
    return jsonify({'success': True, 'item': item.to_dict()})


@api_menu_bp.route('/items/<int:item_id>', methods=['DELETE'])
@staff_required
def delete_item(item_id):
    """Delete a menu item."""
    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Item deleted'})
