from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.request_quota import RequestQuota
from app.models.chat import Chat
from app.utils.logger import get_logger

# Create users Blueprint
users = Blueprint('users', __name__)

logger = get_logger(__name__)

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

@users.route('/quota', methods=['GET'])
@jwt_required()
def get_quota():
    current_user = get_jwt_identity()
    remaining = RequestQuota.get_remaining_requests(current_user)

    logger.info(f"User {current_user} has {remaining} requests remaining")

    return jsonify({
        "remaining_requests": remaining,
        "max_requests": 15,
        "reset_time": "midnight UTC"
    })

@users.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_user():
    current_user_id = get_jwt_identity()

    # Find the user in database
    user = User.objects.get(id=current_user_id)

    if not user:
        return {'message': 'User not found'}, 404

    # Delete user's chat history
    Chat.objects(user_id=current_user_id).delete()

    # Delete user's request quota
    RequestQuota.objects(user_id=current_user_id).delete()

    # Delete user
    user.delete()

    logger.info(f"User {current_user_id} and associated data deleted successfully")

    return {'message': 'User and associated data deleted successfully'}, 200