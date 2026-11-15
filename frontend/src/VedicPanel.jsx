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
}) {
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
      <div
        style={{
          marginTop: 8,
          display: "flex",
          gap: 12,
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
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
      </div>
      {notice && (
        <div
          style={{
            marginTop: 8,
            padding: 8,
            background: "#fff4e5",
            border: "1px solid #f0c36d",
            borderRadius: 4,
          }}
        >
          <strong>{notice.reason_code}:</strong> {notice.detail}
          {notice.fallback_endpoint && (
            <div style={{ fontSize: 12, marginTop: 4 }}>
              Fallback: <code>{notice.fallback_endpoint}</code> (MIDI export, in-SPA)
            </div>
          )}
        </div>
      )}
    </div>
  );
}
