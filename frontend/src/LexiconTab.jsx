import { useState } from "react";
import { API_URL } from "./config";

export default function LexiconTab() {
  const [text, setText] = useState("dharma");
  const [result, setResult] = useState(null);
  const [semantic, setSemantic] = useState(null);
  const [loading, setLoading] = useState(false);

  const lookup = async () => {
    const query = text.trim();
    if (!query) return;
    setLoading(true);
    setResult(null);
    setSemantic(null);

    try {
      const [morphRes, semRes] = await Promise.all([
        fetch(`${API_URL}/api/v3/lexicon/lookup`, {
          method: "POST",
          headers: { "Content-Type": "application/json; charset=utf-8" },
          body: JSON.stringify({ text: query }),
        }),
        fetch(`${API_URL}/api/v3/lexicon/semantic?stem=${encodeURIComponent(query)}`),
      ]);

      setResult(await morphRes.json());
      if (semRes.ok) {
        setSemantic(await semRes.json());
      }
    } catch (e) {
      setResult({ error: String(e) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", color: "#e2e8f0" }}>
      <h1 style={{ color: "#a78bfa" }}>Live Lexicon (Kośa) & Nirukta Lookup</h1>
      <p style={{ color: "#94a3b8" }}>
        Attest a stem against the Pāṇinian dictionary and semantic dhātu index
      </p>

      <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && lookup()}
          placeholder="e.g., dharma, karma, rāma, deva"
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
              <h2 style={{ color: "#4ade80", marginTop: 0 }}>✓ Morphologically Attested</h2>
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
              <h2 style={{ color: "#fbbf24", marginTop: 0 }}>Not Morphologically Attested</h2>
              <p style={{ color: "#94a3b8" }}>{result.message}</p>
            </>
          )}
        </div>
      )}

      {semantic && (
        <div style={{
          background: "#1e293b", padding: "20px", borderRadius: "10px",
          marginTop: "20px",
          border: semantic.found ? "1px solid #38bdf8" : "1px solid #475569",
        }}>
          {semantic.found ? (
            <>
              <h2 style={{ color: "#38bdf8", marginTop: 0 }}>
                Semantic & Nirukta Metadata ({semantic.stem})
              </h2>
              <div style={{
                display: "grid", gridTemplateColumns: "1fr 1fr",
                gap: "10px", marginTop: "15px",
              }}>
                {[
                  ["Dhātu", semantic.dhatu],
                  ["Gaṇa", semantic.gana && `${semantic.gana} (Gaṇa ${semantic.gana_number})`],
                  ["Nirukta", semantic.nirukta],
                  ["Gloss", semantic.gloss],
                ].map(([label, val]) => val != null && (
                  <div key={label} style={{
                    padding: "10px", background: "#0f172a", borderRadius: "6px",
                  }}>
                    <div style={{ color: "#64748b", fontSize: "12px" }}>{label}</div>
                    <div style={{ color: "#e2e8f0" }}>{String(val)}</div>
                  </div>
                ))}
              </div>
              {semantic.synonyms?.length > 0 && (
                <div style={{ marginTop: "12px", padding: "10px", background: "#0f172a", borderRadius: "6px" }}>
                  <div style={{ color: "#64748b", fontSize: "12px" }}>Synonyms (Paryāya)</div>
                  <div style={{ color: "#a78bfa" }}>{semantic.synonyms.join(" · ")}</div>
                </div>
              )}
              {semantic.citations?.length > 0 && (
                <div style={{ marginTop: "10px", padding: "10px", background: "#0f172a", borderRadius: "6px" }}>
                  <div style={{ color: "#64748b", fontSize: "12px" }}>Canonical Citations</div>
                  <div style={{ color: "#94a3b8" }}>{semantic.citations.join(" · ")}</div>
                </div>
              )}
            </>
          ) : (
            <p style={{ color: "#94a3b8", margin: 0 }}>
              No semantic/nirukta record indexed for <strong>{text}</strong> yet (54 core stems currently indexed).
            </p>
          )}
        </div>
      )}
    </div>
  );
}