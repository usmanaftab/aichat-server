from flask import Flask
from flask_mongoengine import MongoEngine
from flask_jwt_extended import JWTManager
from app.config import Config
from app.utils.email import mail
from dotenv import load_dotenv
import os
from flask_cors import CORS

load_dotenv()

db = MongoEngine()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['MONGODB_HOST'] = os.getenv('MONGODB_URI')

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    # Register blueprints
    from app.routes.auth import auth
    app.register_blueprint(auth, url_prefix='/api/auth')
    
    from app.routes.users import users
    app.register_blueprint(users, url_prefix='/api/users')

    # Add this to test the connection
    @app.route('/test-db')
    def test_db():
        try:
            db.connection.server_info()
            return 'Connected to MongoDB!'
        except Exception as e:
            return f'Failed to connect to MongoDB: {str(e)}'

    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000"],
            "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
            "supports_credentials": True
        }
    })

    return app
