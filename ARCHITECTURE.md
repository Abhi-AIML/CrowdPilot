# CrowdPilot Architecture

```mermaid
graph TD
    subgraph "Frontend (Vanilla JS + HTML5)"
        UI[User Dashboard]
        Maps[Google Maps JS API + Heatmap]
        Chat[AI Concierge UI]
        SSE_Client[EventSource SSE Client]
    end

    subgraph "Backend (Flask + Python 3.11)"
        App[Flask App Factory]
        Auth[Firebase Auth Middleware]
        SSE_Service[SSE Broadcast Service]
        Blueprints[API/Dashboard/AI Blueprints]
    end

    subgraph "AI & External Services"
        Gemini[Gemini 1.5 Flash - google-genai]
        Firebase[Firebase Firestore + Auth]
        Simulation[Crowd Data Simulator]
    end

    UI --> Blueprints
    SSE_Client -- "Listen (/api/stream)" --> SSE_Service
    Blueprints --> Gemini
    Blueprints --> Firebase
    Simulation -- "Real-time Density" --> Firebase
    Firebase -- "Change Feed" --> SSE_Service
    SSE_Service -- "Notification" --> SSE_Client
    SSE_Client --> Maps
```

## System Flow
1.  **Authentication**: Users log in via Firebase. A "Judge Login" bypasses the auth flow for demonstrations.
2.  **Heatmap Updates**: A background simulator logic (or Firestore listeners) updates crowd density. These changes are streamed to the frontend via Server-Sent Events (SSE).
3.  **Real-time Alerts**: The SSE stream allows the backend to push emergency banners instantly to all connected users.
4.  **AI Safety**: The "CrowdPilot Assistant" checks all messages for emergency keywords. If found, it triggers a system bypass to provide immediate safety instructions without AI latency.
5.  **Smart Exit**: Based on stadium congestion, the app dynamically reveals the Exit Planner 15 minutes before the event concludes.
