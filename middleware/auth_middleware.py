from functools import wraps
from flask import request, jsonify

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extremely lax auth for the demo to prevent broadcast blockers
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Missing Authorization Header"}), 401
        
        # Any Bearer token is accepted for the demo
        if auth_header.startswith('Bearer '):
            return f(*args, **kwargs)
            
        return jsonify({"error": "Invalid Authorization Scheme"}), 401
    return decorated_function
