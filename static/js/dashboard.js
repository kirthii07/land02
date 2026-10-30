let sensorChart = null;
let dashMap = null;
let dashStationMarker = null;
let dashGISLayers = { landslide: null, agriculture: null, forest: null };


// ========================================
// LOAD LATEST DATA
// ========================================

async function loadLatestData() {

    try {

        const response = await fetch("/api/latest");
        const result = await response.json();

        if (!result.success || !result.data) {
            return;
        }

        const data = result.data;

        // Sensor values
        setTextSafe("rainfall", Number(data.rainfall).toFixed(1));
        setTextSafe("soilMoisture", Number(data.soil_moisture).toFixed(1));
        setTextSafe("tilt", Number(data.tilt).toFixed(2));
        setTextSafe("temperature", Number(data.temperature).toFixed(1));
        setTextSafe("humidity", Number(data.humidity).toFixed(1));

        // Location
        setTextSafe("location", data.location || "Unknown");

        // SHI
        const shi = Number(data.shi || 0);
        setTextSafe("shi", shi.toFixed(0));
        setTextSafe("shiCard", shi.toFixed(0));

        // Risk
        updateRiskDisplay(data.risk_level, shi);

        // Risk card value
        setTextSafe("riskCardValue", data.risk_level || "UNKNOWN");
        colorizeRiskText("riskCardValue", data.risk_level);

        // Time
        if (data.timestamp) {
            const date = new Date(data.timestamp);
            setTextSafe("lastUpdated", "Updated: " + date.toLocaleString());
        }

    } catch (error) {
        console.error("Latest data error:", error);
    }
}


// ========================================
// HELPER: SAFE SET TEXT
// ========================================

function setTextSafe(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function colorizeRiskText(id, risk) {
    const el = document.getElementById(id);
    if (!el) return;
    const colors = {
        "LOW": "#047857",
        "MODERATE": "#d97706",
        "HIGH": "#ea580c",
        "CRITICAL": "#dc2626"
    };
    el.style.color = colors[(risk || "").toUpperCase()] || "#0f2419";
}


// ========================================
// RISK DISPLAY
// ========================================

function updateRiskDisplay(risk, shi) {

    const riskElement = document.getElementById("riskLevel");
    const statusElement = document.getElementById("statusRisk");

    if (riskElement) riskElement.textContent = risk || "UNKNOWN";
    if (statusElement) statusElement.textContent = risk || "UNKNOWN";

    // SHI gauge
    const degree = Math.min(shi, 100) * 3.6;
    const circle = document.querySelector(".shi-circle");

    if (circle) {
        let gaugeColor = "#047857";
        if (risk === "MODERATE") gaugeColor = "#d97706";
        else if (risk === "HIGH") gaugeColor = "#ea580c";
        else if (risk === "CRITICAL") gaugeColor = "#dc2626";

        circle.style.background =
            `conic-gradient(
                ${gaugeColor} 0deg,
                ${gaugeColor} ${degree}deg,
                #e5e7eb ${degree}deg
            )`;
    }

    // Risk colors
    const riskColors = {
        "LOW": "#047857",
        "MODERATE": "#d97706",
        "HIGH": "#ea580c",
        "CRITICAL": "#dc2626"
    };

    const color = riskColors[risk] || "#0f2419";

    if (riskElement) riskElement.style.color = color;
    if (statusElement) statusElement.style.color = color;
}


// ========================================
// LOAD HISTORY
// ========================================

async function loadHistory() {

    try {

        const response = await fetch("/api/history?limit=20");
        const result = await response.json();

        if (!result.success) return;

        const data = result.data.reverse();

        updateChart(data);

        if (data.length > 0) {
            updateFactorsAndRecommendations(data[data.length - 1]);
        }

    } catch (error) {
        console.error("History error:", error);
    }
}


// ========================================
// UPDATE CHART
// ========================================

function updateChart(data) {

    const canvas = document.getElementById("sensorChart");
    if (!canvas) return;

    const labels = data.map(item => {
        const date = new Date(item.timestamp);
        return date.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
        });
    });

    const rainfall = data.map(item => Number(item.rainfall));
    const moisture = data.map(item => Number(item.soil_moisture));
    const shi = data.map(item => Number(item.shi));

    if (sensorChart) {
        sensorChart.destroy();
    }

    sensorChart = new Chart(canvas, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Rainfall (mm)",
                    data: rainfall,
                    borderColor: "#047857",
                    backgroundColor: "rgba(4, 120, 87, 0.1)",
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true
                },
                {
                    label: "Soil Moisture (%)",
                    data: moisture,
                    borderColor: "#2563eb",
                    backgroundColor: "rgba(37, 99, 235, 0.08)",
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true
                },
                {
                    label: "SHI",
                    data: shi,
                    borderColor: "#d97706",
                    backgroundColor: "rgba(217, 119, 6, 0.08)",
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        padding: 16,
                        usePointStyle: true,
                        font: { size: 12 }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: "#e5ebe8" }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}


// ========================================
// FACTORS + RECOMMENDATIONS
// ========================================

async function updateFactorsAndRecommendations(latest) {

    try {

        const response = await fetch("/api/risk");
        const result = await response.json();

        if (!result.success) return;

        const risk = result.risk;

        const factorContainer = document.getElementById("riskFactors");
        const recommendationContainer = document.getElementById("recommendations");

        // Factors
        if (factorContainer) {
            factorContainer.innerHTML = "";

            if (!risk.risk_factors || risk.risk_factors.length === 0) {
                factorContainer.innerHTML =
                    `<div class="empty-state">
                        No major risk factors detected.
                    </div>`;
            } else {
                risk.risk_factors.forEach(factor => {
                    const item = document.createElement("div");
                    item.className = "factor-item";
                    item.innerHTML = `
                        <span>${factor.factor}</span>
                        <span class="factor-severity ${factor.severity.toLowerCase()}">
                            ${factor.severity}
                        </span>
                    `;
                    factorContainer.appendChild(item);
                });
            }
        }

        // Recommendations
        if (recommendationContainer) {
            recommendationContainer.innerHTML = "";

            if (!risk.recommendations || risk.recommendations.length === 0) {
                recommendationContainer.innerHTML =
                    `<div class="empty-state">
                        No recommendations available.
                    </div>`;
            } else {
                risk.recommendations.forEach(recommendation => {
                    const item = document.createElement("div");
                    item.className = "recommendation-item";
                    item.textContent = "✓ " + recommendation;
                    recommendationContainer.appendChild(item);
                });
            }
        }

    } catch (error) {
        console.error("Risk data error:", error);
    }
}


// ========================================
// DASHBOARD MINI MAP
// ========================================

async function initDashboardMap() {
    const mapEl = document.getElementById("dashboardMiniMap");
    if (!mapEl) return;

    dashMap = L.map("dashboardMiniMap", {
        center: [22.3511, 78.6677],
        zoom: 5,
        minZoom: 4,
        maxZoom: 14,
        zoomControl: true,
        scrollWheelZoom: true
    });

    L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}", {
        attribution: "Tiles &copy; Esri &mdash; USGS, GIS Community",
        maxZoom: 18
    }).addTo(dashMap);

    // Initialize GIS layer groups
    dashGISLayers.landslide = L.layerGroup().addTo(dashMap);
    dashGISLayers.agriculture = L.layerGroup();
    dashGISLayers.forest = L.layerGroup();

    // Load GIS layers
    try {
        const res = await fetch("/api/gis/layers");
        const data = await res.json();
        if (data.success && data.layers) {
            if (data.layers.landslide) {
                L.geoJSON(data.layers.landslide, {
                    style: function(feature) {
                        return {
                            color: feature.properties.color || "#dc2626",
                            weight: 1.5,
                            fillColor: feature.properties.color || "#dc2626",
                            fillOpacity: 0.22
                        };
                    },
                    onEachFeature: function(feature, layer) {
                        const p = feature.properties;
                        layer.bindPopup(`
                            <strong>${p.name}</strong><br>
                            <span style="color: #b91c1c; font-weight: 600;">${p.susceptibility}</span><br>
                            <span style="font-size: 11px; color: #475569;">${p.state}</span>
                        `);
                    }
                }).addTo(dashGISLayers.landslide);
            }
        }
    } catch (e) {
        console.error("Dashboard GIS load error:", e);
    }

    // Load monitoring station marker
    try {
        const res = await fetch("/api/location");
        const data = await res.json();
        if (data.success && data.location) {
            const loc = data.location;
            const lat = loc.latitude || 11.685;
            const lon = loc.longitude || 76.132;
            const risk = (loc.risk_level || "LOW").toUpperCase();

            let color = "#10b981";
            if (risk === "MODERATE") color = "#f59e0b";
            else if (risk === "HIGH") color = "#ea580c";
            else if (risk === "CRITICAL") color = "#dc2626";

            const icon = L.divIcon({
                className: "dash-station-icon",
                html: `<div style="background: ${color}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid #fff; box-shadow: 0 0 8px ${color};"></div>`,
                iconSize: [14, 14],
                iconAnchor: [7, 7]
            });

            dashStationMarker = L.marker([lat, lon], { icon: icon }).addTo(dashMap);
            dashStationMarker.bindPopup(`
                <strong>ESP32 Field Station</strong><br>
                ${loc.name}<br>
                <span style="font-weight: 600;">Risk: ${risk}</span>
            `);
        }
    } catch (e) {
        console.error("Dashboard station marker error:", e);
    }

    // Click handler for dashboard map
    dashMap.on("click", function(e) {
        window.location.href = `/map`;
    });
}


// ========================================
// INITIAL LOAD
// ========================================

async function loadDashboard() {
    await loadLatestData();
    await loadHistory();
}


// ========================================
// AUTO REFRESH + INIT
// ========================================

document.addEventListener("DOMContentLoaded", function() {
    loadDashboard();
    initDashboardMap();
});

setInterval(loadDashboard, 5000);
