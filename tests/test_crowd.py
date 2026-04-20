import json

def test_crowd_heatmap_schema(client):
    """Verify the heatmap snapshot contains correctly formatted zones."""
    response = client.get('/api/crowd/heatmap')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert 'zones' in data
    assert len(data['zones']) > 0
    
    zone = data['zones'][0]
    required_keys = ['zone_id', 'density', 'lat', 'lng', 'alert_level']
    for key in required_keys:
        assert key in zone
    
    assert 0 <= zone['density'] <= 100

def test_crowd_sse_stream_header(client):
    """Verify the SSE endpoint returns correct headers."""
    response = client.get('/api/crowd/stream')
    assert response.headers['Content-Type'] == 'text/event-stream'

def test_crowd_history(client):
    """Verify history endpoint returns 60 items."""
    response = client.get('/api/crowd/history')
    data = json.loads(response.data)
    assert len(data['history']) == 60
