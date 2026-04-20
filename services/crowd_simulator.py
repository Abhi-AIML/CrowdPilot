"""
CrowdPilot Crowd Simulator — M. Chinnaswamy Stadium, Bengaluru

Simulates realistic IPL match crowd patterns across 8 stadium zones.
Time-of-day curve mirrors the June 2024 RCB celebration crowd dynamics
where Gate 1 (M.G. Road) reached critical density without any early
warning system in place.

This module provides deterministic but realistic density values that
change over time, driving the live heatmap and zone timer displays.
"""
from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone


# ============================================================
# DEMO CONTEXT — M. Chinnaswamy Stadium, Bengaluru
# ============================================================
# June 4, 2024: After RCB's IPL victory, 35,000+ fans gathered
# outside the stadium for a celebration parade. Gate 1 on M.G.
# Road experienced a critical crowd surge with no early warning
# system in place, resulting in injuries and panic.
#
# CrowdPilot would have:
#   1. Detected the Gate 1 density spike 12+ min early (>80% alert)
#   2. Broadcast a staff alert and attendee warning banner
#   3. Redirected attendees to Gate 2 (Cubbon Park, 38% density)
#   4. AI concierge would answer "which gate?" with live data
#   5. Exit planner would have shown Gate 2 as safest option
# ============================================================

# ---------------------------------------------------------------------------
# Zone definitions — real approximate GPS for Chinnaswamy Stadium, Bengaluru
# ---------------------------------------------------------------------------

ZONES_CONFIG: list[dict] = [
    {
        "zone_id": "gate_1",
        "name": "Gate 1 — M.G. Road Entry",
        "lat": 12.97958, "lng": 77.60059,
        "base_capacity": 0.72,   # historically most congested
        "description": "Primary east entrance off M.G. Road. "
                        "Site of the 2024 crowd surge incident.",
        "is_accessible": True,
        "category": "gate",
    },
    {
        "zone_id": "gate_2",
        "name": "Gate 2 — Cubbon Park Side",
        "lat": 12.98012, "lng": 77.59880,
        "base_capacity": 0.38,   # quieter alternate route
        "description": "Recommended alternate entry. Consistently lower density.",
        "is_accessible": True,
        "category": "gate",
    },
    {
        "zone_id": "gate_3",
        "name": "Gate 3 — KSCA Club House",
        "lat": 12.97842, "lng": 77.59845,
        "base_capacity": 0.45,
        "description": "South entry near KSCA club house.",
        "is_accessible": False,
        "category": "gate",
    },
    {
        "zone_id": "gate_4",
        "name": "Gate 4 — North Entry",
        "lat": 12.98098, "lng": 77.59982,
        "base_capacity": 0.40,
        "description": "North stand entry. Moderate capacity.",
        "is_accessible": True,
        "category": "gate",
    },
    {
        "zone_id": "main_concourse",
        "name": "Main Concourse",
        "lat": 12.97920, "lng": 77.59960,
        "base_capacity": 0.55,
        "description": "Central circulation spine connecting all gates.",
        "is_accessible": True,
        "category": "concourse",
    },
    {
        "zone_id": "food_court",
        "name": "Food Court — West Stand",
        "lat": 12.97885, "lng": 77.59812,
        "base_capacity": 0.50,
        "description": "Main food and beverage area. Peaks at halftime.",
        "is_accessible": True,
        "category": "food",
    },
    {
        "zone_id": "north_stand",
        "name": "North Stand Approach",
        "lat": 12.98105, "lng": 77.59958,
        "base_capacity": 0.62,
        "description": "High-capacity stand. Approaches critical at kickoff.",
        "is_accessible": False,
        "category": "stand",
    },
    {
        "zone_id": "parking_exit",
        "name": "Parking & Exit Zone",
        "lat": 12.97762, "lng": 77.59990,
        "base_capacity": 0.28,
        "description": "South parking area. Surges sharply post-match.",
        "is_accessible": True,
        "category": "parking",
    },
]

# ---------------------------------------------------------------------------
# Time-of-day crowd curve
# (minutes_from_kickoff, density_multiplier)
# ---------------------------------------------------------------------------

CROWD_CURVE: list[tuple[int, float]] = [
    (-120, 0.12), (-90, 0.22), (-60, 0.40), (-45, 0.58),
    (-30, 0.72), (-15, 0.88), (-5, 0.94), (0, 0.97),
    (15, 0.82), (45, 0.76), (85, 0.88),   # halftime surge
    (100, 0.75), (120, 0.72), (145, 0.60),
    (150, 0.99), (155, 0.95),              # post-match rush (peak risk)
    (170, 0.82), (190, 0.55), (210, 0.30),
]

# Demo: simulate kickoff at a fixed offset so heatmap shows interesting state
# In production this would be set from the events API
_SIMULATED_KICKOFF_OFFSET_MINS: int = -25   # currently 25 min before kickoff

# In-memory store for previous snapshot (for trend calculation)
_previous_densities: dict[str, float] = {}
_last_snapshot_time: float = 0.0


@dataclass
class CrowdZone:
    """Represents the real-time crowd state of one stadium zone."""
    zone_id: str
    name: str
    lat: float
    lng: float
    density: int                   # 0-100 percentage
    trend: str                     # "rising" | "falling" | "stable"
    alert_level: str               # "low" | "medium" | "high" | "critical"
    description: str
    is_accessible: bool
    category: str
    wait_mins: int                 # estimated wait to enter this zone
    people_count: int              # estimated current occupancy
    updated_at: str                # ISO8601 timestamp


def _interpolate_curve(minutes_from_kickoff: float) -> float:
    """Linearly interpolate the crowd curve for the given time offset."""
    if minutes_from_kickoff <= CROWD_CURVE[0][0]:
        return CROWD_CURVE[0][1]
    if minutes_from_kickoff >= CROWD_CURVE[-1][0]:
        return CROWD_CURVE[-1][1]
    for i in range(len(CROWD_CURVE) - 1):
        t0, v0 = CROWD_CURVE[i]
        t1, v1 = CROWD_CURVE[i + 1]
        if t0 <= minutes_from_kickoff <= t1:
            ratio = (minutes_from_kickoff - t0) / (t1 - t0)
            return v0 + ratio * (v1 - v0)
    return 0.5


def _classify_alert(density: int) -> str:
    if density >= 90:
        return "critical"
    if density >= 75:
        return "high"
    if density >= 50:
        return "medium"
    return "low"


def _estimate_wait(density: int, category: str) -> int:
    """Estimate queue wait in minutes based on density and zone type."""
    base = {"gate": 6, "food": 4, "concourse": 2, "stand": 3, "parking": 8}.get(category, 4)
    return max(1, round(base * math.exp(density / 45)))


def get_snapshot() -> dict:
    """
    Generate a realistic crowd snapshot for all Chinnaswamy zones.

    Returns:
        Dict containing zones list, event_phase, updated_at, and
        summary stats used by the frontend dashboard cards.
    """
    global _previous_densities, _last_snapshot_time

    # Simulate time progression for demo
    elapsed_since_start = (time.time() % 3600) / 60   # cycles every hour
    mins_from_kickoff = _SIMULATED_KICKOFF_OFFSET_MINS + elapsed_since_start
    curve_multiplier = _interpolate_curve(mins_from_kickoff)

    # Determine event phase
    if mins_from_kickoff < -15:
        phase = "pre_match"
    elif mins_from_kickoff < 0:
        phase = "gates_open"
    elif 85 <= mins_from_kickoff <= 105:
        phase = "halftime"
    elif mins_from_kickoff > 148:
        phase = "egress"
    else:
        phase = "live"

    now_iso = datetime.now(timezone.utc).isoformat()
    zones_out: list[dict] = []

    for cfg in ZONES_CONFIG:
        zid = cfg["zone_id"]
        # Base density = zone capacity × curve multiplier × slight noise
        noise = random.uniform(-0.04, 0.04)
        raw = cfg["base_capacity"] * curve_multiplier + noise

        # Gate 1 extra load for Chinnaswamy realism
        if zid == "gate_1" and phase in ("gates_open", "pre_match", "egress"):
            raw = min(raw * 1.28, 0.98)
        # Gate 2 stays quieter (demonstrates alternate routing value)
        if zid == "gate_2":
            raw = max(raw * 0.65, 0.08)
        # Food court spikes at halftime
        if zid == "food_court" and phase == "halftime":
            raw = min(raw * 1.35, 0.95)
        # Parking surges at egress
        if zid == "parking_exit" and phase == "egress":
            raw = min(raw * 1.45, 0.99)

        density = max(5, min(99, round(raw * 100)))
        prev = _previous_densities.get(zid, density)
        diff = density - prev

        if diff > 3:
            trend = "rising"
        elif diff < -3:
            trend = "falling"
        else:
            trend = "stable"

        zone = CrowdZone(
            zone_id=zid,
            name=cfg["name"],
            lat=cfg["lat"],
            lng=cfg["lng"],
            density=density,
            trend=trend,
            alert_level=_classify_alert(density),
            description=cfg["description"],
            is_accessible=cfg["is_accessible"],
            category=cfg["category"],
            wait_mins=_estimate_wait(density, cfg["category"]),
            people_count=round(density * 3.5),
            updated_at=now_iso,
        )
        zones_out.append(asdict(zone))
        _previous_densities[zid] = density

    _last_snapshot_time = time.time()

    # Summary stats for dashboard cards
    densities = [z["density"] for z in zones_out]
    min_wait = min(z["wait_mins"] for z in zones_out if z["category"] == "gate")
    critical_zones = [z["name"] for z in zones_out if z["alert_level"] in ("high","critical")]

    return {
        "zones": zones_out,
        "event_phase": phase,
        "mins_from_kickoff": round(mins_from_kickoff),
        "average_density": round(sum(densities) / len(densities)),
        "peak_zone": max(zones_out, key=lambda z: z["density"])["name"],
        "min_gate_wait_mins": min_wait,
        "critical_zones": critical_zones,
        "updated_at": now_iso,
    }
