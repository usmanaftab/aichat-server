import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    MONGODB_SETTINGS = {
        'host': os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/my_app'
    }
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    WEB_CLIENT_URL = os.environ.get('WEB_CLIENT_URL')
    MONGODB_HOST = os.environ.get('MONGODB_URI')
    OAUTH_CREDENTIALS = {
        'google': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET')
        }
    }
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'your-email@example.com')
