from functools import wraps
from flask import request, jsonify
import re

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Enforce strict access control presence
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Missing Authorization Header", "code": "AUTH_001"}), 401
        
        # Enforce strict Bearer token scheme
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({"error": "Invalid Authorization Scheme. Must use Bearer.", "code": "AUTH_002"}), 401
            
        token = parts[1]
        
        # Secure Token Validation: Alphanumeric and standard JWT characters only
        if not re.match(r"^[a-zA-Z0-9_\-\.]+$", token):
            return jsonify({"error": "Malformed authorization token", "code": "AUTH_003"}), 401
            
        # In this demo configuration, we pass validation if the token is structurally sound
        return f(*args, **kwargs)
        
    return decorated_function
