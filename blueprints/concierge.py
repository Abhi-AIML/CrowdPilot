from flask import Blueprint, request, jsonify
from services.gemini_service import chat_with_concierge
from services.crowd_simulator import get_snapshot
import html

concierge_bp = Blueprint('concierge', __name__)

@concierge_bp.route('/api/concierge/chat', methods=['POST'])
def chat():
    # Security: Validate JSON presence
    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400
        
    message = data.get('message', '')
    
    # Security: Strict type mapping and length validation to prevent overflow/injection
    if not isinstance(message, str):
        return jsonify({"error": "Message must be a string"}), 400
        
    if len(message) > 500:
        return jsonify({"error": "Message exceeds maximum allowed length"}), 400
        
    message = message.strip()
    if not message:
        return jsonify({"error": "Message payload cannot be empty"}), 400
        
    # Security: Basic XSS sanitization before passing to LLM
    sanitized_message = html.escape(message)
    
    # Inject live stadium state into the AI context
    current_state = get_snapshot()
    
    response = chat_with_concierge(sanitized_message, stadium_context=current_state)
    return jsonify(response)
