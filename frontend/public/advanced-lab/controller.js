(function () {
    "use strict";

    const GUARDRAILS = [
        "Isolation: Advanced Lab files live under /advanced-lab.html and /advanced-lab/* without altering Sanskrit Engine, Canon, Cabinet, Mantra, Gandharva, or /quanta/ behavior.",
        "Honest Status: Modules marked SPEC / LAB or EXPERIMENTAL are design/scaffolding placeholders until independently executed and verified.",
        "QEC & M3 Separation: M3 readout mitigation addresses readout assignment errors (permitting negative quasi-probabilities) and does not replace QEC decoding.",
        "Reversible Arithmetic: Zero logical garbage means clean ancilla return and disentanglement in noiseless simulation, not zero physical energy dissipation."
    ];

    function renderGuardrails() {
        const container = document.getElementById("lab-guardrail-summary");
        if (!container) return;

        const list = document.createElement("ul");
        list.className = "lab-guardrail-list";

        for (const itemText of GUARDRAILS) {
            const li = document.createElement("li");
            li.textContent = itemText;
            list.appendChild(li);
        }

        container.replaceChildren(list);
    }

    function markActiveSubnav() {
        const currentPath = window.location.pathname;
        const links = document.querySelectorAll(".lab-subnav .studio-tab-link");
        for (const link of links) {
            const href = link.getAttribute("href");
            if (href && href === currentPath) {
                link.classList.add("is-active");
                link.setAttribute("aria-current", "page");
            }
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function () {
            renderGuardrails();
            markActiveSubnav();
        });
    } else {
        renderGuardrails();
        markActiveSubnav();
    }
})();