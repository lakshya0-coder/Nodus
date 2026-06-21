from flask import Flask, request, session, current_app
from app.config import Config
from app.models import db
from app.services import i18n
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'error'

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    # Initialize i18n
    i18n.init_app(app)

    # Context processor for templates
    @app.context_processor
    def inject_global_vars():
        lang = session.get('lang', request.cookies.get('lang', 'en'))
        
        def translate(key):
            return i18n.get_translation(key, lang)
            
        return {
            'lang': lang,
            '_': translate
        }
        
    @app.route('/set-language/<lang_code>')
    def set_language(lang_code):
        from flask import redirect, request, make_response
        if lang_code in ['en', 'hi']:
            session['lang'] = lang_code
            resp = redirect(request.referrer or '/')
            resp.set_cookie('lang', lang_code, max_age=60*60*24*30) # 30 days
            return resp
        return redirect(request.referrer or '/')

    with app.app_context():
        # Create all database tables
        db.create_all()

        # Register Blueprints
        from app.routes.public import public_bp
        from app.routes.menu_routes import menu_bp
        from app.routes.booking_routes import booking_bp
        from app.routes.auth import auth_bp
        from app.routes.admin import admin_bp
        
        from app.routes.api_ai import api_ai_bp
        from app.routes.api_bookings import api_bookings_bp
        from app.routes.api_orders import api_orders_bp
        from app.routes.api_menu import api_menu_bp
        from app.routes.api_ml import api_ml_bp

        app.register_blueprint(public_bp)
        app.register_blueprint(menu_bp)
        app.register_blueprint(booking_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp)
        
        app.register_blueprint(api_ai_bp, url_prefix='/api/ai')
        app.register_blueprint(api_bookings_bp, url_prefix='/api/bookings')
        app.register_blueprint(api_orders_bp, url_prefix='/api/orders')
        app.register_blueprint(api_menu_bp, url_prefix='/api/menu')
        app.register_blueprint(api_ml_bp, url_prefix='/api/ml')

    return app
