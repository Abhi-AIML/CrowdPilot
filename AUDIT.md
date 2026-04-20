# CrowdPilot System Audit (Audit-Agent)

This audit evaluates the current partial codebase against the target specifications.

## 1. Structure Audit
- [ ] **app.py**: Currently initialization is inside `app/__init__.py`. Needs migration to a root-level `app.py` with the `create_app()` factory pattern.
- [ ] **Blueprints**: Currently using flat filenames like `api_bp.py`. Needs reorganization into `blueprints/` folder with domain-specific naming (`crowd.py`, `concierge.py`, etc.).
- [ ] **Services**: Partially separated but need to follow the `services/` directory structure strictly.
- [ ] **Utils**: Missing `sse_helpers.py` and `validators.py`.

## 2. SDK Audit (CRITICAL)
- [x] **SDK Version**: Successfully using `from google import genai` (google-genai v0.8.0).
- [ ] **Model Name**: Currently using `gemini-3.1-flash-lite-preview`. Recommend switching to `gemini-1.5-flash` for stability as per target instructions.
- [x] **Import Check**: No instances of deprecated `google.generativeai` found.

## 3. Security Audit
- [x] **Secrets**: API keys are correctly managed via `.env`.
- [ ] **Firebase Auth**: JWT verification is missing from `POST` and `api/` endpoints. Needs `auth_middleware.py`.
- [x] **CORS**: Configured in `app/__init__.py`.
- [x] **Rate Limiting**: Configured globally, but needs specific decorators for concierge and report endpoints.
- [ ] **Input Validation**: Missing robust sanitization for chat and reports.

## 4. Map Audit (CRITICAL)
- [x] **API Loading**: Loaded with visualization library.
- [x] **Heatmap**: Initialized, but radius and gradient need optimization for "premium" look.
- [ ] **TrafficLayer**: Missing. Must be added and set to toggleable.
- [ ] **SSE Wiring**: Basic wiring present, but needs to handle complex "Zone Snapshot" payloads.
- [ ] **Custom Overlays**: Currently using standard Google markers. Needs full rewrite to `ZoneOverlay` class for animated pulsing rings and floating info cards.
- [ ] **Hybrid Mode**: Currently using satellite view without enough hybrid labels.

## 5. Missing Features Checklist
- [ ] **Specific SSE Routes**: Missing `/api/crowd/stream` and `/api/alerts/stream`.
- [ ] **Crowd Simulator**: Current simulation is basic jitter. Needs full `crowd_simulator.py` with Chinnaswamy GPS data and the time-of-day curve.
- [ ] **Staff Dashboard**: Missing `/staff` route and `staff.html`.
- [ ] **Exit Planner**: Basic UI exists but lacks real-time multi-step logic.
- [ ] **Pytest Suite**: Current tests are minimal and lack mocked Firebase/Gemini with 80% coverage.

## 6. Fix Priority Order
1. **CRITICAL**: Reorganize project structure to match the target architecture.
2. **CRITICAL**: Implement `crowd_simulator.py` and `sse_helpers.py`.
3. **HIGH**: Implement `auth_middleware.py` and protect endpoints.
4. **HIGH**: Rewrite `map.js` for the Operatons Centre feel.
5. **MEDIUM**: Build the Staff Dashboard and related APIs.
6. **MEDIUM**: Complete the Pytest suite with 80% coverage.
