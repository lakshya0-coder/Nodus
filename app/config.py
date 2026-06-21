import os

basedir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(os.path.dirname(basedir), 'instance')


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'nodus-cafe-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(instance_dir, "nodus_cafe.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cafe defaults
    CAFE_NAME = 'Nodus Cafe'
    CAFE_DEFAULT_CAPACITY = 30
    CAFE_OPEN_HOUR = 8   # 8 AM
    CAFE_CLOSE_HOUR = 22  # 10 PM
    CAFE_SLOT_DURATION = 60  # minutes

    # ML config
    ML_MODEL_DIR = os.path.join(os.path.dirname(basedir), 'ml', 'models')
    ML_MIN_BOOKINGS_FOR_TRAINING = 50
    ML_RETRAIN_DAY = 'sun'  # Day of week for weekly retraining
    ML_RETRAIN_HOUR = 0     # Hour (midnight)

    # AI config
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

    # Upload config
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'images', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max upload


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
