// Known-Good Sandhi Verification Card (deterministic audit)
(function () {
  const CASES = [
    { left: "a",     right: "i",     expect: "e" },
    { left: "a",     right: "u",     expect: "o" },
    { left: "vidyā", right: "ālaya", expect: "vidyālaya" },
    { left: "rāma",  right: "iti",   expect: "rāmeti" },
    { left: "deva",  right: "indra", expect: "devendra" },
  ];

  async function run() {
    const tbody = document.getElementById("sandhi-golden-body");
    if (!tbody) return;
    const apiBase = (typeof API_BASE !== "undefined" && API_BASE) || "https://api.aigaane.in";
    const rows = [];
    for (const c of CASES) {
      try {
        const r = await fetch(apiBase + "/api/v3/sandhi/combine", {
          method: "POST",
          headers: { "Content-Type": "application/json; charset=utf-8" },
          body: JSON.stringify({ left: c.left, right: c.right }),
        });
        const data = await r.json();
        const cand = (data.candidates && data.candidates[0]) || {};
        const got = cand.surface || "\u2014";
        const sutra = cand.sutra || "\u2014";
        rows.push({ left: c.left, right: c.right, expect: c.expect, got, sutra, pass: got === c.expect });
      } catch (e) {
        rows.push({ left: c.left, right: c.right, expect: c.expect, got: "ERROR", sutra: "\u2014", pass: false });
      }
    }
    tbody.innerHTML = rows.map(function (r) {
      const color = r.pass ? "#4ade80" : "#f87171";
      const bg = r.pass ? "#14532d" : "#7f1d1d";
      const txt = r.pass ? "#4ade80" : "#fca5a5";
      const label = r.pass ? "PASS" : "FAIL";
      return (
        '<tr style="border-top:1px solid #1e293b;">' +
          '<td style="padding:8px;color:#e2e8f0;">' + r.left + "</td>" +
          '<td style="padding:8px;color:#e2e8f0;">' + r.right + "</td>" +
          '<td style="padding:8px;color:#94a3b8;">' + r.expect + "</td>" +
          '<td style="padding:8px;color:' + color + ';">' + r.got + "</td>" +
          '<td style="padding:8px;color:#a78bfa;">' + r.sutra + "</td>" +
          '<td style="padding:8px;">' +
            '<span style="padding:2px 8px;border-radius:4px;font-size:12px;background:' + bg + ';color:' + txt + ';">' +
              label +
            "</span>" +
          "</td>" +
        "</tr>"
      );
    }).join("");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();