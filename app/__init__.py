from flask import Flask
from flask_mongoengine import MongoEngine
from flask_jwt_extended import JWTManager
from app.config import Config
from app.utils.email import mail
from app.utils.logger import setup_logger, get_logger
from dotenv import load_dotenv
import os
from flask_cors import CORS

load_dotenv()

db = MongoEngine()
jwt = JWTManager()
logger = get_logger(__name__)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['MONGODB_HOST'] = os.getenv('MONGODB_URI')

    # Setup logging
    setup_logger(app)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    # Log startup information
    logger.info('Application starting up...')
    logger.debug(f'MongoDB URI: {os.getenv("MONGODB_URI", "Not set")}')

    # Register blueprints
    from app.routes.auth import auth
    from app.routes.users import users
    from app.routes.chat import chat
    
    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(users, url_prefix='/api/users')
    app.register_blueprint(chat, url_prefix='/api/chat')

    # Add this to test the connection
    @app.route('/test-db')
    def test_db():
        try:
            db.connection.server_info()
            logger.info('Successfully connected to MongoDB')
            return 'Connected to MongoDB!'
        except Exception as e:
            logger.error(f'Failed to connect to MongoDB: {str(e)}')
            return f'Failed to connect to MongoDB: {str(e)}'

    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000", "https://usmanaftab.github.io"],
            "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
            "supports_credentials": True
        }
    })

    logger.info('Application setup completed')
    return app
