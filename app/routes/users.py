from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

# Create users Blueprint
users = Blueprint('users', __name__)

@users.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    # Get the user ID from the JWT token
    current_user_id = get_jwt_identity()
    
    # Find the user in database
    user = User.objects.get(id=current_user_id)
    
    if not user:
        return {'message': 'User not found'}, 404
        
    # Return user profile data
    return {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'oauth_provider': user.oauth_provider if hasattr(user, 'oauth_provider') else None
    }, 200 