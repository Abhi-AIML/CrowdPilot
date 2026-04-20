/**
 * CrowdPilot Map & Real-time Module
 * =====================
 * Handles Google Maps visualization and SSE data routing to dashboard components.
 */

'use strict';

const CHINNASWAMY = { lat: 12.97920, lng: 77.59960 };
const MAP_ZOOM = 17;
const SSE_URL = '/api/crowd/stream';

let map = null;
let heatmapLayer = null;
let trafficLayer = null;
let directionsService = null;
let directionsRenderer = null;
let zoneOverlays = [];
let sseSource = null;

// Initialize global state to prevent early-click errors
window.currentZonesData = [];

// Alert level colors
const ALERT_COLORS = {
  low:      { fill: '#10b981', stroke: '#059669', text: '#000000' },
  medium:   { fill: '#f59e0b', stroke: '#d97706', text: '#000000' },
  high:     { fill: '#ef4444', stroke: '#b91c1c', text: '#FFFFFF' },
  critical: { fill: '#b91c1c', stroke: '#7f1d1d', text: '#FFFFFF' },
};

function initMap() {
    const mapEl = document.getElementById('map-canvas');
    if (!mapEl) return;

    map = new google.maps.Map(mapEl, {
        center: CHINNASWAMY,
        zoom: MAP_ZOOM,
        mapTypeId: 'hybrid',
        disableDefaultUI: true,
        styles: [
            { featureType: 'poi', stylers: [{ visibility: 'off' }] },
            { featureType: 'transit', stylers: [{ visibility: 'off' }] },
        ]
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
        polylineOptions: {
            strokeColor: '#10b981',
            strokeWeight: 6,
            strokeOpacity: 0.8
        },
        suppressMarkers: false
    });

    heatmapLayer = new google.maps.visualization.HeatmapLayer({
        data: [],
        map: map,
        radius: 40,
        opacity: 0.8
    });

    trafficLayer = new google.maps.TrafficLayer();
    trafficLayer.setMap(map);

    connectSSE();
}

function connectSSE() {
    if (sseSource) sseSource.close();
    sseSource = new EventSource(SSE_URL);

    sseSource.onmessage = (e) => {
        try {
            const data = JSON.parse(e.data);
            if (data.error) return;
            
            window.currentZonesData = data.zones; // Global store for components
            updateDashboard(data);
            updateHeatmap(data.zones);
            updateZoneOverlays(data.zones);
            updateQueueList(data.zones);
        } catch (err) {
            console.error('[SSE Parse Error]', err);
        }
    };
}

function updateDashboard(data) {
    // Update Stat Cards on Home tab
    const phaseEl = document.getElementById('current-phase');
    const densityEl = document.getElementById('avg-density');
    const safeGateEl = document.getElementById('safe-gate');
    const alertCard = document.getElementById('alert-card');

    if (phaseEl) phaseEl.textContent = data.event_phase.replace('_', ' ').toUpperCase();
    if (densityEl) densityEl.textContent = data.average_density;
    
    // Correctly identify safest gate
    if (safeGateEl && data.zones) {
        const gates = data.zones.filter(z => z.category === 'gate');
        if (gates.length > 0) {
            const safest = gates.sort((a, b) => a.wait_mins - b.wait_mins)[0];
            safeGateEl.textContent = `${safest.wait_mins}m (${safest.name})`;
        }
    }

    // 1. Handle Automatic Critical Zone Alerts
    if (data.critical_zones?.length > 0) {
        if (alertCard) {
            alertCard.style.display = 'flex';
            document.getElementById('alert-zone').textContent = data.critical_zones[0];
            document.getElementById('alert-card').querySelector('.stat-footer').textContent = 'High density surge detected!';
        }
    } else {
        if (alertCard) alertCard.style.display = 'none';
    }

    // 2. Handle Manual Staff Alerts
    if (data.alerts && data.alerts.length > 0) {
        const latest = data.alerts[data.alerts.length - 1];
        const ticker = document.getElementById('alert-ticker');
        if (ticker) {
            ticker.innerHTML = data.alerts.slice(-3).reverse().map(a => `
                <div class="ticker-alert ${a.severity}" style="margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.8rem;">
                    <span class="pulse-dot"></span>
                    <strong>${a.severity.toUpperCase()}:</strong> ${a.message}
                </div>
            `).join('');
        }
        
        if (alertCard && latest.severity === 'emergency') {
            alertCard.style.display = 'flex';
            alertCard.style.background = 'var(--color-danger)';
            document.getElementById('alert-zone').textContent = 'EMERGENCY';
            document.getElementById('alert-card').querySelector('.stat-footer').textContent = latest.message;
        }
    }

    // 3. Update Exit Planner Dynamic Content
    const scoreEl = document.getElementById('safety-score');
    const adviceEl = document.getElementById('exit-advice');
    if (scoreEl && adviceEl) {
        const avg = data.average_density;
        const score = 100 - avg;
        scoreEl.textContent = score + '% ' + (score > 80 ? '(Excellent)' : score > 50 ? '(Good)' : '(Caution)');
        
        const gates = data.zones.filter(z => z.category === 'gate').sort((a,b) => a.wait_mins - b.wait_mins);
        if (gates.length > 0) {
            adviceEl.innerHTML = `Exit via <strong>${gates[0].name}</strong> (${gates[0].wait_mins}m wait) to avoid congestion.`;
        }
    }
}

function updateQueueList(zones) {
    const listEl = document.getElementById('queue-list');
    if (!listEl) return;

    const gates = zones.filter(z => z.category === 'gate').sort((a, b) => a.wait_mins - b.wait_mins);
    
    listEl.innerHTML = gates.map(gate => `
        <div class="queue-item glass" onclick="window.focusZone('${gate.zone_id}')" style="cursor:pointer;">
            <div class="queue-info">
                <h4>${gate.name}</h4>
                <p>${gate.description}</p>
            </div>
            <div class="queue-time">
                <span class="time-val" style="color: ${ALERT_COLORS[gate.alert_level].fill}">${gate.wait_mins} min</span>
                <span class="time-label">Current Wait</span>
            </div>
        </div>
    `).join('');
}

function updateHeatmap(zones) {
    const points = zones.map(z => ({
        location: new google.maps.LatLng(z.lat, z.lng),
        weight: z.density / 100
    }));
    heatmapLayer.setData(points);
}

function updateZoneOverlays(zones) {
    const incomingIds = new Set(zones.map(z => z.zone_id));
    zoneOverlays = zoneOverlays.filter(o => {
        if (!incomingIds.has(o.zoneId)) { o.overlay.setMap(null); return false; }
        return true;
    });

    zones.forEach(zone => {
        const existing = zoneOverlays.find(o => o.zoneId === zone.zone_id);
        if (existing) {
            existing.overlay.updateData(zone);
        } else {
            const overlay = new ZoneOverlay(zone, map);
            zoneOverlays.push({ zoneId: zone.zone_id, overlay });
        }
    });
}

class ZoneOverlay extends google.maps.OverlayView {
    constructor(zoneData, map) {
        super();
        this.data = zoneData;
        this.el = null;
        this.setMap(map);
    }
    onAdd() {
        this.el = document.createElement('div');
        this.el.className = 'zone-overlay';
        this._render();
        this.getPanes().overlayMouseTarget.appendChild(this.el);
    }
    draw() {
        if (!this.el) return;
        const pos = this.getProjection().fromLatLngToDivPixel(new google.maps.LatLng(this.data.lat, this.data.lng));
        this.el.style.left = pos.x + 'px';
        this.el.style.top = pos.y + 'px';
    }
    updateData(d) {
        this.data = d;
        this._render();
    }
    _render() {
        const colors = ALERT_COLORS[this.data.alert_level] || ALERT_COLORS.low;
        const pulse = this.data.alert_level === 'critical' ? 'zone-pin--pulse' : '';
        this.el.innerHTML = `
            <div class="zone-pin ${pulse}" style="--pin-color:${colors.fill}; --pin-stroke:${colors.stroke}">
                <div class="zone-pin__ring"></div>
                <div class="zone-pin__badge" style="background:${colors.fill}; color:${colors.text}">${this.data.density}%</div>
            </div>
        `;
    }
}

window.initMap = initMap;

window.requestNavigation = (lat, lng) => {
    if (!directionsService) {
        console.warn('Directions service not initialized yet.');
        return;
    }

    const start = new google.maps.LatLng(CHINNASWAMY.lat, CHINNASWAMY.lng);
    const end = new google.maps.LatLng(lat, lng);

    const request = {
        origin: start,
        destination: end,
        travelMode: google.maps.TravelMode.WALKING
    };

    directionsService.route(request, (result, status) => {
        if (status === google.maps.DirectionsStatus.OK) {
            directionsRenderer.setDirections(result);
            // Switch to heatmap tab to show the path
            const tabBtn = document.querySelector('[data-tab="heatmap"]');
            if (tabBtn) tabBtn.click();
        } else {
            console.error('Directions request failed due to ' + status);
        }
    });
};

window.focusZone = (id) => {
    const zone = window.currentZonesData?.find(x => x.zone_id === id);
    if (zone) {
        map.panTo({ lat: zone.lat, lng: zone.lng });
        map.setZoom(19);
        document.querySelector('[data-tab="heatmap"]').click();
    }
};

window.generateExitPath = () => {
    // Intelligent Exit: Find safest gate and navigate
    const gates = window.currentZonesData?.filter(z => z.category === 'gate').sort((a,b) => a.wait_mins - b.wait_mins);
    if (gates && gates.length > 0) {
        window.requestNavigation(gates[0].lat, gates[0].lng);
    }
};
