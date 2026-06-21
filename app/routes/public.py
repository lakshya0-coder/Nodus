"""Public page routes — Home, About, Contact."""
from flask import Blueprint, render_template, session, request, jsonify
from app.models.menu import MenuItem, MenuCategory
from app.models.order import Order, OrderItem
from app.models import db
from datetime import datetime

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def home():
    """Home page with featured items."""
    lang = session.get('lang', request.cookies.get('lang', 'en'))

    # Get featured/bestseller items
    featured_items = MenuItem.query.filter(
        MenuItem.is_available == True,
        MenuItem.tags.contains('Bestseller')
    ).limit(6).all()

    # Fallback: if no bestsellers, just get first 6 available items
    if not featured_items:
        featured_items = MenuItem.query.filter_by(is_available=True).limit(6).all()

    featured_dicts = [item.to_dict(lang) for item in featured_items]

    # Testimonials (static for now)
    testimonials = [
        {
            'name': 'Priya Sharma' if lang == 'en' else 'प्रिया शर्मा',
            'text': 'The best coffee I\'ve had in Bangalore! The ambiance is perfect for both work and casual meetups.' if lang == 'en' else 'बैंगलोर में मैंने जो सबसे अच्छी कॉफ़ी पी है! माहौल काम और आराम दोनों के लिए बेहतरीन है।',
            'rating': 5
        },
        {
            'name': 'Rahul Verma' if lang == 'en' else 'राहुल वर्मा',
            'text': 'Their AI recommendation suggested a Lavender Latte and I\'m absolutely hooked. Game changer!' if lang == 'en' else 'उनके AI ने मुझे लैवेंडर लैटे सुझाया और मैं पूरी तरह दीवाना हो गया। शानदार!',
            'rating': 5
        },
        {
            'name': 'Ananya Patel' if lang == 'en' else 'अनन्या पटेल',
            'text': 'Love the seat booking feature! No more waiting in queues. The cold brew here is divine.' if lang == 'en' else 'सीट बुकिंग की सुविधा बहुत पसंद आई! अब लाइन में खड़े होने की ज़रूरत नहीं। कोल्ड ब्रू लाजवाब है।',
            'rating': 5
        }
    ]

    return render_template('home.html',
                         featured_items=featured_dicts,
                         testimonials=testimonials)


@public_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')


@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with form."""
    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        message = request.form.get('message', '')
        
        if name and email and message:
            try:
                from app.models.contact import ContactMessage
                new_msg = ContactMessage(name=name, email=email, message=message)
                db.session.add(new_msg)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error saving contact message: {e}")
                
        return render_template('contact.html', success=True)
    return render_template('contact.html')


@public_bp.route('/api/public/orders', methods=['POST'])
def create_public_order():
    """Create a new order from the public frontend."""
    data = request.get_json()
    if not data or not data.get('items'):
        return jsonify({'error': 'Invalid order data'}), 400

    try:
        order = Order(
            order_ref=Order.generate_ref(),
            customer_name=data.get('customer_name', 'Guest'),
            notes=data.get('table_number', 'Takeaway'),
            status='received',
            total_amount=0.0
        )
        db.session.add(order)
        db.session.flush()

        total = 0.0
        for item_data in data['items']:
            menu_item = MenuItem.query.get(item_data['menu_item_id'])
            if menu_item:
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=menu_item.id,
                    quantity=item_data['quantity'],
                    unit_price=menu_item.price,
                    special_instructions=item_data.get('notes', '')
                )
                db.session.add(order_item)
                total += float(menu_item.price) * item_data['quantity']

        order.total_amount = total
        db.session.commit()
        return jsonify({'success': True, 'order_ref': order.order_ref})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
