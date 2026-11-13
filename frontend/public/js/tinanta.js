// Verb Conjugation panel (Q4-B) — deterministic tiṅanta generation
(function () {
  const PURUSHAS = [
    ["prathama_purusha", "Prathamā (3rd)"],
    ["madhyama_purusha", "Madhyamā (2nd)"],
    ["uttama_purusha",   "Uttamā (1st)"],
  ];
  const VACANAS = ["ekavacana", "dvivacana", "bahuvacana"];

  async function renderTinanta() {
    const dhatu  = document.getElementById("tin-dhatu")?.value;
    const lakara = document.getElementById("tin-lakara")?.value;
    const pada   = document.getElementById("tin-pada")?.value;
    const body   = document.getElementById("tinanta-body");
    const hint   = document.getElementById("tin-hint");
    if (!dhatu || !lakara || !pada || !body) return;

    body.innerHTML = '<tr><td colspan="4" style="color:#94a3b8;padding:8px;">Loading…</td></tr>';
    if (hint) hint.textContent = "Generating " + dhatu + " · " + lakara + " · " + pada + "…";

    const apiBase = (typeof API_BASE !== "undefined" && API_BASE) || "https://api.aigaane.in";
    const url = apiBase + "/api/v3/morphology/tinanta/paradigm?dhatu=" + encodeURIComponent(dhatu) + "&lakara=" + encodeURIComponent(lakara) + "&pada=" + encodeURIComponent(pada);

    try {
      const r = await fetch(url);
      if (!r.ok) throw new Error("HTTP " + r.status);
      const data = await r.json();
      if (data.error) throw new Error(data.error);

      const rows = PURUSHAS.map(function (pair) {
        const key = pair[0], label = pair[1];
        const cells = VACANAS.map(function (vac) {
          const rowForPurusha = (data.rows || []).find(function (row) { return row.purusha === key; });
          const cell = rowForPurusha ? (rowForPurusha.cells || []).find(function (c) { return c.vacana === vac; }) : null;
          const surface = (cell && cell.surface) ? cell.surface : "—";
          const source = (cell && cell.source) ? cell.source : "";
          const badge = source === "table"
            ? ' <span style="color:#4ade80;font-size:10px;">✓</span>'
            : source === "generated"
              ? ' <span style="color:#fbbf24;font-size:10px;">~</span>'
              : '';
          return '<td style="padding:8px;color:#e2e8f0;font-family:\'Noto Serif\',serif;">' + surface + badge + '</td>';
        }).join("");
        return '<tr style="border-top:1px solid #1e293b;"><td style="padding:8px;color:#94a3b8;">' + label + '</td>' + cells + '</tr>';
      }).join("");

      body.innerHTML = rows;
      if (hint) {
        if (data.unverified || (data.error && data.source === 'unsupported')) {
          hint.innerHTML = '⚠ <strong>' + data.dhatu + '</strong> · ' + data.lakara + ' · ' + data.pada +
            ' — <span style="color:#fbbf24;">' + (data.warning || data.error || 'not yet verified') + '</span>';
        } else {
          var noteHtml = data.usage_note
            ? '<br><span style="color:#fbbf24;font-size:12px;">ⓘ ' + data.usage_note + '</span>'
            : '';
          hint.innerHTML = '✓ <strong>' + data.dhatu + '</strong> · ' + data.lakara + ' · ' + data.pada + ' — gaṇa ' + data.gana + '. ' +
            '<span style="color:#4ade80;">✓</span> verified &nbsp; <span style="color:#fbbf24;">~</span> generated' + noteHtml;
        }
      }
    } catch (e) {
      body.innerHTML = '<tr><td colspan="4" style="color:#f87171;padding:8px;">Error: ' + e.message + '</td></tr>';
      if (hint) hint.textContent = "Generation failed.";
    }
  }

  window.renderTinanta = renderTinanta;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", renderTinanta);
  } else {
    renderTinanta();
  }
})();