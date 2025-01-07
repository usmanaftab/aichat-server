from functools import wraps
from flask import jsonify, request, make_response
from flask_jwt_extended import get_jwt_identity
from app.models.request_quota import RequestQuota
from app.utils.logger import get_logger

logger = get_logger(__name__)

def check_request_quota(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        
        if not current_user:
            return jsonify({"error": "Authentication required"}), 401
            
        remaining = RequestQuota.get_remaining_requests(current_user)
        
        if remaining <= 0:
            logger.warning(f"User {current_user} has exceeded their daily request quota")
            return jsonify({
                "error": "Daily request quota exceeded",
                "remaining_requests": 0,
                "reset_time": "midnight UTC"
            }), 429
            
        if not RequestQuota.increment_request_count(current_user):
            logger.warning(f"Failed to increment request count for user {current_user}")
            return jsonify({"error": "Failed to process request"}), 500
            
        # Pass remaining requests to the decorated function
        response = f(*args, **kwargs)
        
        # Convert response to a response object if it isn't already
        if isinstance(response, tuple):
            response_obj = make_response(response[0])
            response_obj.status_code = response[1]
            if len(response) > 2:
                response_obj.headers.extend(response[2])
        else:
            response_obj = make_response(response)
            
        # Add rate limit header
        response_obj.headers['X-RateLimit-Remaining'] = str(remaining - 1)
        
        return response_obj
        
    return decorated_function