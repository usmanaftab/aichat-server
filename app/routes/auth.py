from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.utils.email import send_reset_password_email
from app.utils.security import generate_reset_token
from datetime import datetime, timedelta
import requests

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.objects(email=data['email']).first():
        return {'message': 'Email already registered'}, 400

    user = User(
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name']
    )
    user.set_password(data['password'])
    user.save()

    return {'message': 'User registered successfully'}, 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.objects(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return {'message': 'Invalid email or password'}, 401

    access_token = create_access_token(identity=str(user.id))
    return {'access_token': access_token}, 200

@auth.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    user = User.objects(email=data['email']).first()

    if not user:
        return {'message': 'Email not found'}, 404

    token = generate_reset_token()
    user.reset_password_token = token
    user.reset_password_expires = datetime.utcnow() + timedelta(hours=1)
    user.save()

    send_reset_password_email(user.email, token)
    return {'message': 'Reset password instructions sent to email'}, 200

@auth.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    user = User.objects(reset_password_token=data['token']).first()

    if not user or user.reset_password_expires < datetime.utcnow():
        return {'message': 'Invalid or expired reset token'}, 400

    user.set_password(data['password'])
    user.reset_password_token = None
    user.reset_password_expires = None
    user.save()

    return {'message': 'Password reset successfully'}, 200

@auth.route('/oauth/google', methods=['POST'])
def google_oauth():
    data = request.get_json()
    token = data['token']

    # Verify Google token
    google_response = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {token}'}
    )

    if google_response.status_code != 200:
        return {'message': 'Invalid token'}, 401

    google_data = google_response.json()
    user = User.objects(email=google_data['email']).first()

    if not user:
        user = User(
            email=google_data['email'],
            first_name=google_data.get('given_name', ''),
            last_name=google_data.get('family_name', ''),
            oauth_provider='google',
            oauth_id=google_data['sub']
        )
        user.save()

    access_token = create_access_token(identity=str(user.id))
    return {'access_token': access_token}, 200
