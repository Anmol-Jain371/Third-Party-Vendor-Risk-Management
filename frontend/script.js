// ---------------------------------------------------
// Vendor Risk Intelligence Landing Page JavaScript
// Modern Interactive Sandbox & Scroll Reveal Features
// ---------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    // 1. Fetch GRC counter metrics
    fetchGRCMetrics();

    // 2. Initialize Scroll Reveal animations
    initScrollReveal();

    // 3. Initialize Interactive Sandbox Simulators (Hero and Main Section)
    initSandboxes();

    // 4. Initialize Interactive Screenshot Showcase
    initShowcase();
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
    const metricsConfig = [
        { id: "metric-vendors", target: metrics.total_vendors, format: (val) => Math.round(val) },
        { id: "metric-high-risk", target: metrics.high_risk_vendors, format: (val) => Math.round(val) },
        { id: "metric-expired", target: metrics.expired_certifications, format: (val) => Math.round(val) },
        { id: "metric-spend", target: metrics.financial_exposure_m, format: (val) => `€${val.toFixed(1)}M` }
    ];

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
        const easeProgress = progress * (2 - progress); // easeOutQuad
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

// 2. Scroll Reveal implementation using Intersection Observer
function initScrollReveal() {
    const revealElements = document.querySelectorAll(".reveal-up");
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                observer.unobserve(entry.target); // Reveal once
            }
        });
    }, {
        threshold: 0.15,
        rootMargin: "0px 0px -50px 0px"
    });

    revealElements.forEach(el => observer.observe(el));
}

// 3. Risk Calculation Engine and Sync logic
function calculateScore(dataAccess, exposure, soc2, mfa, leastPrivilege) {
    // Base score from access level
    let base = 25;
    if (dataAccess === 2) base = 45;
    if (dataAccess === 3) base = 65;

    // Financial exposure contribution (0 to 25 points max)
    const exposurePoints = (exposure / 100) * 25;
    let score = base + exposurePoints;

    // Deduct points for active security safeguards
    if (soc2) score -= 22;
    if (mfa) score -= 12;
    if (leastPrivilege) score -= 11;

    // Floor and Ceiling bounds
    score = Math.max(8, Math.min(98, score));
    return Math.round(score);
}

function updateGaugeUI(gaugeId, scoreValId, labelId, score) {
    const scoreValEl = document.getElementById(scoreValId);
    const labelEl = document.getElementById(labelId);
    const gaugeEl = document.getElementById(gaugeId);

    if (!scoreValEl || !labelEl || !gaugeEl) return;

    // Update text
    scoreValEl.textContent = score;

    // Determine category, color, and status label
    let color = "#10b981"; // green
    let label = "Low";
    if (score >= 40 && score < 70) {
        color = "#f59e0b"; // amber
        label = "Medium";
    } else if (score >= 70) {
        color = "#ef4444"; // red
        label = "High";
    }

    labelEl.textContent = label;
    labelEl.style.color = color;

    // Update conic gradient background
    gaugeEl.style.background = `conic-gradient(${color} 0% ${score}%, #e2e8f0 ${score}% 100%)`;
}

function initSandboxes() {
    // A. Hero Sandbox Elements
    const heroAccess = document.getElementById("slider-data-access");
    const heroExposure = document.getElementById("slider-exposure");
    const heroSoc2 = document.getElementById("check-soc2");
    const heroMfa = document.getElementById("check-mfa");

    const textDataAccess = document.getElementById("val-data-access");
    const textExposure = document.getElementById("val-exposure");

    function updateHeroSandbox() {
        if (!heroAccess || !heroExposure) return;

        const accessVal = parseInt(heroAccess.value);
        const exposureVal = parseInt(heroExposure.value);
        const hasSoc2 = heroSoc2 ? heroSoc2.checked : false;
        const hasMfa = heroMfa ? heroMfa.checked : false;

        // Update labels
        const accessLabel = accessVal === 1 ? "Low" : accessVal === 2 ? "Medium" : "High";
        if (textDataAccess) textDataAccess.textContent = accessLabel;
        if (textExposure) textExposure.textContent = `€${exposureVal}M`;

        // Calculate
        const score = calculateScore(accessVal, exposureVal, hasSoc2, hasMfa, true);
        
        // Update UI
        updateGaugeUI("gauge-conic", "sandbox-score-val", "sandbox-score-label", score);
    }

    if (heroAccess) {
        [heroAccess, heroExposure, heroSoc2, heroMfa].forEach(ctrl => {
            if (ctrl) ctrl.addEventListener("input", updateHeroSandbox);
            if (ctrl) ctrl.addEventListener("change", updateHeroSandbox);
        });
        updateHeroSandbox();
    }

    // B. Main Sandbox Section Elements
    const mainAccess = document.getElementById("sandbox-access");
    const mainExposure = document.getElementById("sandbox-exposure");
    const mainSoc2 = document.getElementById("sandbox-soc2");
    const mainMfa = document.getElementById("sandbox-mfa");
    const mainPrivileged = document.getElementById("sandbox-privileged");

    const detailAccess = document.getElementById("detail-data-access");
    const detailExposure = document.getElementById("detail-exposure");
    const driversList = document.getElementById("risk-drivers-list");

    function updateMainSandbox() {
        if (!mainAccess || !mainExposure) return;

        const accessVal = parseInt(mainAccess.value);
        const exposureVal = parseInt(mainExposure.value);
        const hasSoc2 = mainSoc2 ? mainSoc2.checked : false;
        const hasMfa = mainMfa ? mainMfa.checked : false;
        const hasPrivilege = mainPrivileged ? mainPrivileged.checked : false;

        // Update text labels
        const accessLabel = accessVal === 1 ? "Low Access" : accessVal === 2 ? "Medium Access" : "High Access";
        if (detailAccess) detailAccess.textContent = accessLabel;
        if (detailExposure) detailExposure.textContent = `€${exposureVal}M`;

        // Calculate score
        const score = calculateScore(accessVal, exposureVal, hasSoc2, hasMfa, hasPrivilege);

        // Update Gauge
        updateGaugeUI("main-gauge-conic", "main-score-val", "main-score-label", score);

        // Dynamically build risk driver bullet points
        if (driversList) {
            driversList.innerHTML = "";
            let drivers = [];

            if (accessVal === 3) drivers.push("High network & data access scope stages elevated threat levels.");
            if (accessVal === 2) drivers.push("Moderate integration level exposes internal subsystems.");
            if (exposureVal > 50) drivers.push("Significant financial exposure multiplies business liability.");
            
            // Positive remediations or pending drivers
            if (!hasSoc2) drivers.push("Absence of active SOC 2 / ISO certification leaves compliance gap.");
            if (!hasMfa) drivers.push("Disabled MFA exposes identity parameters to compromise.");
            if (!hasPrivilege) drivers.push("Lack of Zero-Trust privilege controls risks lateral movement.");

            if (drivers.length === 0) {
                drivers.push("All major safeguards active. Risk containment operating at peak efficiency.");
            }

            drivers.forEach(drv => {
                const li = document.createElement("li");
                li.textContent = drv;
                driversList.appendChild(li);
            });
        }
    }

    if (mainAccess) {
        [mainAccess, mainExposure, mainSoc2, mainMfa, mainPrivileged].forEach(ctrl => {
            if (ctrl) ctrl.addEventListener("input", updateMainSandbox);
            if (ctrl) ctrl.addEventListener("change", updateMainSandbox);
        });
        updateMainSandbox();
    }
}

// 4. Interactive Showcase Screen Switcher
function initShowcase() {
    const tabButtons = document.querySelectorAll(".tab-btn");
    const screenImages = document.querySelectorAll(".showcase-screen-img");

    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            // Remove active class from buttons
            tabButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            // Hide all images
            const targetId = btn.getAttribute("data-target");
            screenImages.forEach(img => {
                img.classList.remove("active");
                if (img.id === targetId) {
                    img.classList.add("active");
                }
            });
        });
    });
}
