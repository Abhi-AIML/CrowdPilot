from services.gemini_service import chat_with_concierge

def test_emergency_bypass_fire():
    """Verify that 'fire' keyword triggers emergency response instantly."""
    response = chat_with_concierge("There is a fire in the north stand!")
    assert response["type"] == "emergency_alert"
    assert "EMERGENCY DETECTED" in response["response"]
    assert response["bypass"] is True

def test_emergency_bypass_medical():
    """Verify that 'heart attack' keyword triggers emergency response."""
    response = chat_with_concierge("Help, my friend is having a heart attack near gate 1")
    assert response["type"] == "emergency_alert"
    assert "medical teams have been alerted" in response["response"].lower()
    assert response["bypass"] is True

def test_ai_fallback_on_no_api_key(monkeypatch):
    """Verify graceful fallback when API key is missing."""
    monkeypatch.setenv("GOOGLE_GENAI_API_KEY", "")
    response = chat_with_concierge("How do I find food?")
    assert response["type"] == "info"
    assert "offline mode" in response["response"]
