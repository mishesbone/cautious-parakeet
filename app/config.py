import os
import secrets
from flask.cli import FlaskGroup
import pymysql  

class Config:
    # Flask Core Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    USER_APP_NAME = 'PAYROLL'
    TEMPLATE_FOLDER= "templates"
    STATIC_FOLDER= "static"
    DEBUG = False
    TESTING = False
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', secrets.token_hex(32))
    WTF_CSRF_ENABLED = True  # Enable CSRF protection by default

    # SQLAlchemy Configuration - Using MySQL with pymysql
    SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URL', "mysql+pymysql://admin:admin@localhost:3306/pms"
)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'itsmishesbone@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = MAIL_USERNAME
    MAIL_MAX_EMAILS = None
    MAIL_ASCII_ATTACHMENTS = False
    MAIL_SUPPRESS_SEND = False
    MAIL_DEBUG = DEBUG

    # Flask-Login Configuration
    SESSION_PROTECTION = 'strong'
    REMEMBER_COOKIE_NAME = 'remember_token'
    REMEMBER_COOKIE_DURATION = 604800  # 1 week in seconds

    # Application-Specific Configuration
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', secrets.token_hex(32))

    # File Upload Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

    # Pagination Configuration
    ITEMS_PER_PAGE = 10

    # Logging Configuration
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')

    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL',  "mysql+pymysql://admin:admin@localhost:3307/pms"
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL', 'sqlite:///testing.db'
    )


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'PROD_DATABASE_URL', "mysql+pymysql://admin:admin@localhost:3307/pms"
    )


# Configuration Mapping
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}

# Determine the Active Configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app_config = config_map[config_name]
