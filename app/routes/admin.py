"""Admin panel routes – dashboard, orders, bookings, menu, predictions, conversations, staff, settings."""

from functools import wraps
from datetime import date, datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import login_required, current_user

from app.models import db
from app.models.user import User
from app.models.order import Order
from app.models.booking import Booking
from app.models.menu import MenuCategory, MenuItem
from app.models.conversation import Conversation
from app.models.prediction import DemandPrediction, ModelVersion
from app.models.setting import Setting

admin_bp = Blueprint('admin', __name__, template_folder='../templates')


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------

def admin_required(f):
    """Ensure the current user is logged-in AND has an admin-level role."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def developer_required(f):
    """Ensure the current user is a developer."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_developer:
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@admin_bp.route('/')
@admin_required
def dashboard():
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    # Stats
    todays_bookings = Booking.query.filter(Booking.date == today).count()
    todays_orders = Order.query.filter(
        Order.created_at >= today_start, Order.created_at <= today_end
    ).count()
    revenue = db.session.query(db.func.coalesce(db.func.sum(Order.total_amount), 0)).filter(
        Order.created_at >= today_start, Order.created_at <= today_end,
        Order.status != 'cancelled'
    ).scalar()

    total_capacity = int(Setting.get('total_capacity', '30'))
    confirmed_guests = db.session.query(
        db.func.coalesce(db.func.sum(Booking.guest_count), 0)
    ).filter(
        Booking.date == today,
        Booking.status.in_(['confirmed', 'completed'])
    ).scalar()
    occupancy = round((confirmed_guests / total_capacity) * 100) if total_capacity else 0

    # Weekly bookings for chart (Mon-Sun)
    week_start = today - timedelta(days=today.weekday())
    weekly_bookings = []
    for i in range(7):
        d = week_start + timedelta(days=i)
        count = Booking.query.filter(Booking.date == d).count()
        weekly_bookings.append({'day': d.strftime('%a'), 'date': d.isoformat(), 'count': count})

    stats = {
        'todays_bookings': todays_bookings,
        'todays_orders': todays_orders,
        'revenue': round(revenue, 2),
        'occupancy': min(occupancy, 100),
        'total_capacity': total_capacity,
        'weekly_bookings': weekly_bookings,
    }

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    upcoming_bookings = Booking.query.filter(
        Booking.date >= today,
        Booking.status.in_(['pending', 'confirmed'])
    ).order_by(Booking.date.asc(), Booking.time_slot.asc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_orders=recent_orders,
        upcoming_bookings=upcoming_bookings,
    )


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

@admin_bp.route('/orders')
@admin_required
def orders():
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    menu_items = MenuItem.query.filter_by(is_available=True).order_by(MenuItem.name_en).all()
    return render_template('admin/orders.html', orders=all_orders, menu_items=menu_items)


# ---------------------------------------------------------------------------
# Bookings
# ---------------------------------------------------------------------------

@admin_bp.route('/bookings')
@admin_required
def bookings():
    all_bookings = Booking.query.order_by(Booking.date.desc(), Booking.time_slot.desc()).all()
    return render_template('admin/bookings.html', bookings=all_bookings)


# ---------------------------------------------------------------------------
# Menu Management
# ---------------------------------------------------------------------------

@admin_bp.route('/menu')
@admin_required
def menu():
    categories = MenuCategory.query.order_by(MenuCategory.display_order).all()
    items = MenuItem.query.order_by(MenuItem.display_order).all()
    return render_template('admin/menu_manage.html', categories=categories, items=items)


# ---------------------------------------------------------------------------
# Demand Predictions
# ---------------------------------------------------------------------------

@admin_bp.route('/predictions')
@admin_required
def predictions():
    today = date.today()
    week_end = today + timedelta(days=6)
    preds = DemandPrediction.query.filter(
        DemandPrediction.date >= today,
        DemandPrediction.date <= week_end
    ).order_by(DemandPrediction.date, DemandPrediction.time_slot).all()

    model_versions = ModelVersion.query.order_by(ModelVersion.trained_at.desc()).all()
    current_model = ModelVersion.query.filter_by(status='active').first()

    return render_template(
        'admin/predictions.html',
        predictions=preds,
        model_versions=model_versions,
        current_model=current_model,
    )


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

@admin_bp.route('/conversations')
@admin_required
def conversations():
    all_convos = Conversation.query.order_by(Conversation.started_at.desc()).all()
    total = len(all_convos)
    avg_msgs = round(sum(len(c.messages) for c in all_convos) / total, 1) if total else 0
    en_count = sum(1 for c in all_convos if c.language == 'en')
    hi_count = total - en_count

    conv_stats = {
        'total': total,
        'avg_messages': avg_msgs,
        'en_count': en_count,
        'hi_count': hi_count,
    }

    return render_template(
        'admin/conversations.html',
        conversations=all_convos,
        conv_stats=conv_stats,
    )


# ---------------------------------------------------------------------------
# Staff Management
# ---------------------------------------------------------------------------

@admin_bp.route('/staff')
@admin_required
def staff():
    if current_user.is_developer:
        users = User.query.order_by(User.created_at.desc()).all()
    else:
        users = User.query.filter(User.role != 'developer').order_by(User.created_at.desc()).all()
    return render_template('admin/staff.html', users=users)


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

@admin_bp.route('/settings')
@admin_required
def settings():
    all_settings = {s.key: s.value for s in Setting.query.all()}
    return render_template('admin/settings.html', settings=all_settings)
