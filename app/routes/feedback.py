from flask import Blueprint, request, jsonify
from app.utils.email import send_email
from app.config import Config
from flask_jwt_extended import jwt_required
feedback = Blueprint('feedback', __name__)

feedback = Blueprint('feedback', __name__)

@feedback.route('/submit', methods=['POST'])
@jwt_required()
def submit_feedback():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'email', 'message']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Extract data
    name = data['name']
    email = data['email']
    message = data['message']
    
    # Prepare email content
    subject = f"New Feedback from {name}"
    body = f"""
    New feedback received:
    
    From: {name}
    Email: {email}
    
    Message:
    {message}
    """
    
    try:
        send_email(
            email=Config.ADMIN_EMAIL,
            subject=subject,
            body=body
        )
        return jsonify({'message': 'Feedback submitted successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to submit feedback'}), 500 