# Shared Contracts - CrowdPilot

## 1. CrowdZone Object
```json
{
  "zone_id": "string",
  "name": "string",
  "lat": "number",
  "lng": "number",
  "density": "number (0-100)",
  "trend": "rising | falling | stable",
  "alert_level": "low | medium | high | critical",
  "description": "string",
  "is_accessible": "boolean",
  "category": "gate | concourse | food | stand | parking",
  "wait_mins": "number",
  "people_count": "number",
  "updated_at": "ISO8601 string"
}
```

## 2. API Responses
- **GET /api/crowd/stream**: `event-stream` returning `CrowdZone` snapshot.
- **GET /api/crowd/history**: `{"history": [{"timestamp": "string", "zone_id": "string", "density": 0}]}`
- **POST /api/concierge/chat**: `{"response": "string", "type": "ai_response | emergency_alert"}`
- **POST /api/alerts/broadcast**: `{"status": "success", "alert_id": "string"}`

## 3. Firestore Schema (Internal)
- `users`: `{uid, role, alerts_enabled}`
- `alerts`: `{alert_id, message, severity, created_at, active}`
