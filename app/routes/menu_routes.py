"""Menu page routes."""
from flask import Blueprint, render_template, session, request
from app.models.menu import MenuItem, MenuCategory

menu_bp = Blueprint('menu_page', __name__)


@menu_bp.route('/menu')
def menu():
    """Menu page with categories and items."""
    lang = session.get('lang', request.cookies.get('lang', 'en'))

    categories = MenuCategory.query.filter_by(is_active=True)\
        .order_by(MenuCategory.display_order).all()
    items = MenuItem.query.filter_by(is_available=True)\
        .order_by(MenuItem.display_order).all()

    return render_template('menu.html',
                         categories=[c.to_dict(lang) for c in categories],
                         items=[i.to_dict(lang) for i in items])
