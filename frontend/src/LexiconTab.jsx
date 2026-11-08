import { useState } from "react";
import { API_URL } from "./config";

export default function LexiconTab() {
  const [text, setText] = useState("rāma");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const lookup = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v3/lexicon/lookup`, {
        method: "POST",
        headers: { "Content-Type": "application/json; charset=utf-8" },
        body: JSON.stringify({ text }),
      });
      setResult(await res.json());
    } catch (e) {
      setResult({ error: String(e) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", color: "#e2e8f0" }}>
      <h1 style={{ color: "#a78bfa" }}>Lexicon (Kośa) Lookup</h1>
      <p style={{ color: "#94a3b8" }}>Attest a stem against the Pāṇinian dictionary</p>

      <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          style={{
            padding: "10px", flex: 1, borderRadius: "6px",
            border: "1px solid #334155", background: "#1e293b", color: "white",
          }}
        />
        <button
          onClick={lookup}
          disabled={loading}
          style={{
            padding: "10px 20px", background: "#a78bfa", border: "none",
            borderRadius: "6px", fontWeight: "bold", cursor: "pointer",
          }}
        >
          {loading ? "Looking up..." : "Lookup"}
        </button>
      </div>

      {result && (
        <div style={{
          background: "#1e293b", padding: "20px", borderRadius: "10px",
          border: result.found ? "1px solid #4ade80" : "1px solid #fbbf24",
        }}>
          {result.error ? (
            <div style={{ color: "#f87171" }}>Error: {result.error}</div>
          ) : result.found ? (
            <>
              <h2 style={{ color: "#4ade80" }}>✓ Attested</h2>
              <p style={{ color: "#94a3b8" }}>
                Strategy: <strong style={{ color: "#a78bfa" }}>{result.strategy}</strong>{" "}
                ({result.strategies_tried} tried)
              </p>
              {result.analysis && (
                <div style={{
                  display: "grid", gridTemplateColumns: "1fr 1fr",
                  gap: "10px", marginTop: "15px",
                }}>
                  {Object.entries(result.analysis).map(([k, v]) =>
                    v != null && (
                      <div key={k} style={{
                        padding: "10px", background: "#0f172a", borderRadius: "6px",
                      }}>
                        <div style={{ color: "#64748b", fontSize: "12px" }}>{k}</div>
                        <div style={{ color: "#e2e8f0" }}>{String(v)}</div>
                      </div>
                    )
                  )}
                </div>
              )}
            </>
          ) : (
            <>
              <h2 style={{ color: "#fbbf24" }}>Not Attested</h2>
              <p style={{ color: "#94a3b8" }}>{result.message}</p>
            </>
          )}
        </div>
      )}
    </div>
  );
}