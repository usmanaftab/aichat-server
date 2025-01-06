from flask import Flask
from flask_mongoengine import MongoEngine
from flask_jwt_extended import JWTManager
from app.config import Config
from app.utils.email import mail

db = MongoEngine()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    # Register blueprints
    from app.routes.auth import auth
    app.register_blueprint(auth, url_prefix='/api/auth')

    return app
