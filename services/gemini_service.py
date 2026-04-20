"""
CrowdPilot Enhanced Gemini Service
"""
from __future__ import annotations
import os
from google import genai
from google.genai import types

EMERGENCY_KEYWORDS = ["fire", "bomb", "medical", "heart attack", "fight", "stampede", "collapsed"]

def get_gemini_client() -> genai.Client | None:
    api_key = os.getenv('GOOGLE_GENAI_API_KEY')
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

def chat_with_concierge(message: str, stadium_context: dict | None = None) -> dict:
    """
    Enhanced chat with Real-Time Stadium Context awareness.
    """
    message_lower = message.lower()
    
    # 1. Emergency Bypass
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in message_lower:
            return {
                "response": "EMERGENCY DETECTED. Help is on the way. Please stay calm.",
                "type": "emergency_alert",
                "bypass": True
            }

    client = get_gemini_client()
    if not client:
        return {"response": "Offline mode. Check live map.", "type": "info", "bypass": False}

    try:
        # Build Context-Aware System Instruction
        context_str = "No live data available."
        if stadium_context:
            zones = stadium_context.get('zones', [])
            context_str = "\n".join([
                f"- {z['name']}: {z['density']}% density, {z['wait_mins']}m wait. Level: {z['alert_level']}"
                for z in zones
            ])
            avg = stadium_context.get('average_density', 'N/A')
            context_str += f"\nGlobal avg density: {avg}%."

        system_instruction = (
            "You are the CrowdPilot Real-Time Operations Assistant for M. Chinnaswamy Stadium, Bengaluru. "
            "You have access to LIVE stadium data. BE CONCISE and FACTUAL. "
            "NEVER use conversational filler like 'I understand' or 'Hello there'. "
            "If a user asks for navigation, analyze the density and suggest the path with LOWER density. "
            f"\n\nCURRENT STADIUM STATE:\n{context_str}\n\n"
            "Rule: If Gate 1 is high density (>70%), ALWAYS tell them to use Gate 2 or 5."
        )

        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2, # Lower temperature for factual precision
                max_output_tokens=150
            ),
            contents=message
        )

        text = ""
        if response.candidates:
            parts = response.candidates[0].content.parts
            text = "".join([p.text for p in parts if p.text])
        
        return {
            "response": text.strip() or "Ask staff for immediate help.",
            "type": "ai_response",
            "bypass": False
        }
    except Exception as e:
        print(f"[Gemini Error] {e}")
        return {
            "response": "Connection issue. Consult safety map.",
            "type": "fallback",
            "bypass": False
        }
