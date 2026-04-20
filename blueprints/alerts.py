from flask import Blueprint, jsonify, request
from middleware.auth_middleware import require_auth
import time

alerts_bp = Blueprint('alerts', __name__)

# In-memory store for demo alerts
active_alerts = []

@alerts_bp.route('/api/alerts/broadcast', methods=['POST'])
@require_auth
def broadcast():
    data = request.json
    alert = {
        "id": f"alert_{len(active_alerts) + 1}",
        "message": data.get('message'),
        "severity": data.get('severity', 'info'),
        "timestamp": time.time()
    }
    active_alerts.append(alert)
    return jsonify({"status": "success", "alert": alert})

@alerts_bp.route('/api/alerts/active', methods=['GET'])
def get_active():
    return jsonify(active_alerts)
