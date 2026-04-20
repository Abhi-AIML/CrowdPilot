import json
import time
from flask import Blueprint, Response, stream_with_context, current_app, jsonify
from services.crowd_simulator import get_snapshot
from utils.sse_helpers import format_sse
from .alerts import active_alerts

crowd_bp = Blueprint('crowd', __name__)

@crowd_bp.route('/api/crowd/stream')
def crowd_stream():
    """
    Server-Sent Events stream for real-time crowd data.
    Pushes a full zone snapshot every 8 seconds.
    Client map.js listens and updates heatmap + timers live.
    """
    def generate():
        while True:
            try:
                snapshot = get_snapshot()
                snapshot['alerts'] = active_alerts # Inject active alerts
                yield format_sse(json.dumps(snapshot))
                time.sleep(8)
            except GeneratorExit:
                break
            except Exception as exc:
                current_app.logger.error("SSE stream error: %s", exc)
                yield format_sse(json.dumps({"error": "stream_error"}))
                time.sleep(8)

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
        }
    )

@crowd_bp.route('/api/crowd/history')
def crowd_history():
    """
    Returns density history for the last 60 minutes (simulated).
    Used by the staff dashboard line chart.
    """
    # Simple mock for now
    history = []
    for i in range(60):
        history.append({
            "timestamp": time.time() - (i * 60),
            "zone_id": "gate_1",
            "density": 80 + (i % 10)
        })
    return jsonify({"history": history})

@crowd_bp.route('/api/crowd/heatmap')
def crowd_heatmap():
    """Initial snapshot for the map."""
    return jsonify(get_snapshot())
