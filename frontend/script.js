// ---------------------------------------------------
// Vendor Risk Intelligence Landing Page JavaScript
// ---------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    // Fetch metrics from metrics.json and update counters
    fetchGRCMetrics();
});

// Default fallback GRC metrics values
const DEFAULT_METRICS = {
    total_vendors: 400,
    high_risk_vendors: 172,
    expired_certifications: 42,
    financial_exposure_m: 149.5
};

function fetchGRCMetrics() {
    fetch("metrics.json")
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(data => {
            updateAllCounters(data);
        })
        .catch(error => {
            console.warn("Metrics API fetch failed. Using fallback GRC cache: ", error);
            updateAllCounters(DEFAULT_METRICS);
        });
}

function updateAllCounters(metrics) {
    // Define target metrics objects
    const metricsConfig = [
        { id: "metric-vendors", target: metrics.total_vendors, format: (val) => val },
        { id: "metric-high-risk", target: metrics.high_risk_vendors, format: (val) => val },
        { id: "metric-expired", target: metrics.expired_certifications, format: (val) => val },
        { id: "metric-spend", target: metrics.financial_exposure_m, format: (val) => `€${val.toFixed(1)}M` }
    ];

    // Trigger animation for each configured counter element
    metricsConfig.forEach(cfg => {
        const el = document.getElementById(cfg.id);
        if (el) {
            animateValue(el, 0, cfg.target, 1500, cfg.format);
        }
    });
}

// Value easeOutQuad counting animation logic
function animateValue(obj, start, end, duration, formatFn) {
    let startTimestamp = null;
    
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        
        // Easing function: easeOutQuad
        const easeProgress = progress * (2 - progress);
        const currentValue = easeProgress * (end - start) + start;
        
        obj.textContent = formatFn(currentValue);
        
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            obj.textContent = formatFn(end);
        }
    };
    
    window.requestAnimationFrame(step);
}
