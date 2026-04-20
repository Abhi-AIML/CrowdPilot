from flask import Blueprint, jsonify, request
from middleware.auth_middleware import require_auth
import time
import html

alerts_bp = Blueprint('alerts', __name__)

# In-memory store for demo alerts
active_alerts = []

@alerts_bp.route('/api/alerts/broadcast', methods=['POST'])
@require_auth
def broadcast():
    # Security: Validate JSON presence
    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400
        
    message = data.get('message')
    severity = data.get('severity', 'info')
    
    # Security: Strict type checking and validation
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Message is required and must be a string"}), 400
        
    if len(message) > 200:
        return jsonify({"error": "Message exceeds maximum allowed length of 200"}), 400
        
    if severity not in ['info', 'warning', 'emergency']:
        return jsonify({"error": "Invalid severity level"}), 400
        
    # Security: Basic XSS sanitization
    sanitized_message = html.escape(message.strip())
    
    alert = {
        "id": f"alert_{len(active_alerts) + 1}",
        "message": sanitized_message,
        "severity": severity,
        "timestamp": time.time()
    }
    
    # Security: Prevent unbounded memory growth (keep only last 100 alerts)
    if len(active_alerts) > 100:
        active_alerts.pop(0)
        
    active_alerts.append(alert)
    return jsonify({"status": "success", "alert": alert})

@alerts_bp.route('/api/alerts/active', methods=['GET'])
def get_active():
    return jsonify(active_alerts)
