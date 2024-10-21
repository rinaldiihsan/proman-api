from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

def role_required(role_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            if current_user.get('role') != role_name:
                return jsonify({'message': 'Unauthorized access'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator