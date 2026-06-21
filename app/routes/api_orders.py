"""Order Management API endpoints."""
from flask import Blueprint, request, jsonify
from app.models import db
from app.models.order import Order, OrderItem
from app.models.menu import MenuItem
from app.routes.auth import staff_required
from datetime import datetime

api_orders_bp = Blueprint('api_orders', __name__)


@api_orders_bp.route('', methods=['GET'])
@staff_required
def list_orders():
    """List orders with optional filters."""
    status = request.args.get('status')
    date_str = request.args.get('date')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Order.query.order_by(Order.created_at.desc())

    if status:
        query = query.filter_by(status=status)
    if date_str:
        try:
            filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Order.created_at) == filter_date)
        except ValueError:
            pass

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'orders': [o.to_dict() for o in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@api_orders_bp.route('', methods=['POST'])
@staff_required
def create_order():
    """Create a new order."""
    data = request.get_json()
    if not data or not data.get('items'):
        return jsonify({'error': 'Order items required'}), 400

    order = Order(
        order_ref=Order.generate_ref(),
        customer_name=data.get('customer_name', 'Walk-in'),
        status='received',
        notes=data.get('notes', '')
    )
    db.session.add(order)
    db.session.flush()

    for item_data in data['items']:
        menu_item = MenuItem.query.get(item_data.get('menu_item_id'))
        if not menu_item:
            continue

        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            quantity=item_data.get('quantity', 1),
            unit_price=menu_item.price,
            special_instructions=item_data.get('special_instructions', '')
        )
        db.session.add(order_item)

    order.calculate_total()
    db.session.commit()

    return jsonify({
        'success': True,
        'order': order.to_dict()
    }), 201


@api_orders_bp.route('/<int:order_id>', methods=['GET'])
@staff_required
def get_order(order_id):
    """Get order details."""
    order = Order.query.get_or_404(order_id)
    return jsonify({'order': order.to_dict()})


@api_orders_bp.route('/<int:order_id>', methods=['PATCH'])
@staff_required
def update_order(order_id):
    """Update order status."""
    order = Order.query.get_or_404(order_id)
    data = request.get_json()

    if 'status' in data:
        valid_statuses = ['received', 'preparing', 'ready', 'completed', 'cancelled']
        if data['status'] in valid_statuses:
            order.status = data['status']
    if 'notes' in data:
        order.notes = data['notes']

    db.session.commit()
    return jsonify({'success': True, 'order': order.to_dict()})


@api_orders_bp.route('/<int:order_id>', methods=['DELETE'])
@staff_required
def delete_order(order_id):
    """Delete an order."""
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Order deleted'})
