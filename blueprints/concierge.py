from flask import Blueprint, request, jsonify
from services.gemini_service import chat_with_concierge
from services.crowd_simulator import get_snapshot

concierge_bp = Blueprint('concierge', __name__)

@concierge_bp.route('/api/concierge/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    # Inject live stadium state into the AI context
    current_state = get_snapshot()
    
    response = chat_with_concierge(message, stadium_context=current_state)
    return jsonify(response)
