"""
Middleware for authentication and authorization
"""
from functools import wraps
from flask import request, jsonify
from services.auth import get_user_from_token, check_is_director


def require_auth(f):
    """
    Decorator to require authentication for an endpoint
    Adds 'current_user' to kwargs with user data
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'No authorization token provided'
            }), 401

        token = auth_header.split(' ')[1]

        # Validate token and get user
        user = get_user_from_token(token)

        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 401

        # Add user to kwargs
        kwargs['current_user'] = user

        return f(*args, **kwargs)

    return decorated_function


def require_director(f):
    """
    Decorator to require Director of Operations role
    Must be used with @require_auth
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = kwargs.get('current_user')

        if not current_user:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401

        if not current_user.get('is_director', False):
            return jsonify({
                'success': False,
                'error': 'Director of Operations access required'
            }), 403

        return f(*args, **kwargs)

    return decorated_function


def get_current_user():
    """
    Helper function to get current user from request
    Returns None if not authenticated
    """
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return None

    token = auth_header.split(' ')[1]
    return get_user_from_token(token)
