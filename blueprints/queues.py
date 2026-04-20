from flask import Blueprint, jsonify

queues_bp = Blueprint('queues', __name__)

@queues_bp.route('/api/queues/status')
def status():
    return jsonify({"status": "all_clear"})
