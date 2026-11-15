import React from "react";

const RECENSIONS = [
  { id: "rgveda_sakala", label: "Rgveda (Sakala)" },
  { id: "taittiriya", label: "Taittiriya (Krsna Yajur)" },
  { id: "kanva", label: "Kanva (Sukla Yajur)" },
  { id: "madhyandina", label: "Madhyandina (Sukla Yajur)" },
  { id: "samaveda", label: "Samaveda (routes to MIDI export)" },
];

export default function VedicPanel({
  text,
  setText,
  recension,
  setRecension,
  loading,
  playing,
  notice,
  onPlay,
  onStop,
  align,
  setAlign,
  talaList,
  tala,
  setTala,
  bpm,
  onDownload,
  downloading,
  renderInfo,
  drone,
  setDrone,
}) {
  const talaOptions = talaList || [];
  return (
    <div
      className="vedic-panel"
      style={{ marginTop: 24, padding: 16, border: "1px solid #ccc", borderRadius: 8 }}
    >
      <h3 style={{ marginTop: 0 }}>Vedic Chant (Svara Contour)</h3>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste Devanagari with Vedic tone marks, e.g. agnim ile purohitam (with ॑ and ॒)"
        style={{ width: "100%", minHeight: 60, fontFamily: "monospace", fontSize: 16 }}
      />
      <div style={{ marginTop: 8, display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <label>
          Recension:{" "}
          <select value={recension} onChange={(e) => setRecension(e.target.value)}>
            {RECENSIONS.map((r) => (
              <option key={r.id} value={r.id}>
                {r.label}
              </option>
            ))}
          </select>
        </label>
        <button onClick={playing ? onStop : onPlay} disabled={loading}>
          {playing ? "Stop Chant" : loading ? "Loading..." : "Play Vedic Chant"}
        </button>
        <button onClick={onDownload} disabled={downloading || !text.trim()}>
          {downloading ? "Rendering..." : "Download WAV"}
        </button>
        <label style={{ cursor: "pointer", fontSize: 13, color: "#555" }}>
          <input type="checkbox" checked={!!drone} onChange={(e) => setDrone(e.target.checked)} />{" "}
          Drone mix
        </label>
      </div>

      <div style={{ marginTop: 10, display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <label style={{ cursor: "pointer" }}>
          <input type="checkbox" checked={!!align} onChange={(e) => setAlign(e.target.checked)} />{" "}
          Align to Tala (grid rhythm)
        </label>
        {align && (
          <>
            <label>
              Tala:{" "}
              <select value={tala} onChange={(e) => setTala(e.target.value)}>
                {talaOptions.length === 0 && <option value="">Loading...</option>}
                {talaOptions.map((t) => (
                  <option key={t.name} value={t.name}>
                    {t.name} ({t.cycle_length} aksharas)
                  </option>
                ))}
              </select>
            </label>
            <span style={{ fontSize: 12, color: "#555" }}>@ {bpm} BPM (from Tala player)</span>
          </>
        )}
      </div>

      {notice && (
        <div style={{ marginTop: 8, padding: 8, background: "#fff4e5", border: "1px solid #f0c36d", borderRadius: 4 }}>
          <strong>{notice.reason_code}:</strong> {notice.detail}
          {notice.fallback_endpoint && (
            <div style={{ fontSize: 12, marginTop: 4 }}>
              Fallback: <code>{notice.fallback_endpoint}</code> (MIDI export, in-SPA)
            </div>
          )}
        </div>
      )}

      {renderInfo && (
        <div style={{ marginTop: 8, padding: 8, background: "#f0fdf4", border: "1px solid #86efac", borderRadius: 4 }}>
          <strong>✓ WAV ready:</strong> <code style={{ fontSize: 12 }}>{renderInfo.filename}</code>
          <div style={{ fontSize: 11, fontFamily: "ui-monospace, monospace", marginTop: 4 }}>
            sha256: {renderInfo.sha256.slice(0, 16)}… · {renderInfo.duration_sec}s · peak {renderInfo.peak_db} dB · RMS {renderInfo.rms_db} dB
          </div>
          <div style={{ fontSize: 11, color: "#555", marginTop: 2 }}>
            Deterministic: same input × 2 → identical sha256. Regenerate and compare the first 8 hex.
          </div>
        </div>
      )}
    </div>
  );
}
