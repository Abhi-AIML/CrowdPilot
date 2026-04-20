from flask import Blueprint, request, jsonify, session
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/verify', methods=['POST'])
def verify():
    # Mock verification for now
    return jsonify({"status": "success", "uid": "visitor_123"})

@auth_bp.route('/api/auth/visitor', methods=['POST'])
def visitor_login():
    visitor_id = f"visitor_{os.urandom(4).hex()}"
    user_data = {
        "uid": visitor_id,
        "name": "Judge / Guest",
        "email": "judge@example.com",
        "role": "attendee"
    }
    return jsonify({"status": "success", "user": user_data})
