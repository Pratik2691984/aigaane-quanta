import { useState } from "react";
import { API_URL } from "./config";

export default function Studio3Tab() {
  const [pluta, setPluta] = useState(0);
  const [dirgha, setDirgha] = useState(0);
  const [cycle, setCycle] = useState(16);
  const [tStart, setTStart] = useState(0);
  const [laghu, setLaghu] = useState(0);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const verify = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v3/studio3/tala/congruence`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pluta_count: parseInt(pluta),
          dirgha_count: parseInt(dirgha),
          cycle_length: parseInt(cycle),
          t_start: parseInt(tStart),
          laghu_count: parseInt(laghu),
        }),
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
      <h1 style={{ color: "#f472b6" }}>Studio III: Tāla Congruence</h1>
      <p style={{ color: "#94a3b8" }}>
        Verify the Diophantine invariant: 3P + 2D + L + t_start ≡ 17 (mod C)
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "10px", marginBottom: "20px" }}>
        <div>
          <label style={{ display: "block", fontSize: "12px", color: "#94a3b8" }}>Pluta (P)</label>
          <input type="number" value={pluta} onChange={(e) => setPluta(e.target.value)} style={{ width: "100%", padding: "8px", background: "#1e293b", color: "white", border: "1px solid #334155", borderRadius: "4px" }} />
        </div>
        <div>
          <label style={{ display: "block", fontSize: "12px", color: "#94a3b8" }}>Dirgha (D)</label>
          <input type="number" value={dirgha} onChange={(e) => setDirgha(e.target.value)} style={{ width: "100%", padding: "8px", background: "#1e293b", color: "white", border: "1px solid #334155", borderRadius: "4px" }} />
        </div>
        <div>
          <label style={{ display: "block", fontSize: "12px", color: "#94a3b8" }}>Laghu (L)</label>
          <input type="number" value={laghu} onChange={(e) => setLaghu(e.target.value)} style={{ width: "100%", padding: "8px", background: "#1e293b", color: "white", border: "1px solid #334155", borderRadius: "4px" }} />
        </div>
        <div>
          <label style={{ display: "block", fontSize: "12px", color: "#94a3b8" }}>Cycle Length (C)</label>
          <input type="number" value={cycle} onChange={(e) => setCycle(e.target.value)} style={{ width: "100%", padding: "8px", background: "#1e293b", color: "white", border: "1px solid #334155", borderRadius: "4px" }} />
        </div>
        <div>
          <label style={{ display: "block", fontSize: "12px", color: "#94a3b8" }}>Start Offset (t_start)</label>
          <input type="number" value={tStart} onChange={(e) => setTStart(e.target.value)} style={{ width: "100%", padding: "8px", background: "#1e293b", color: "white", border: "1px solid #334155", borderRadius: "4px" }} />
        </div>
        <div style={{ display: "flex", alignItems: "flex-end" }}>
          <button onClick={verify} disabled={loading} style={{ width: "100%", padding: "8px", background: "#f472b6", border: "none", borderRadius: "4px", fontWeight: "bold", cursor: "pointer" }}>
            {loading ? "Verifying..." : "Verify Tāla"}
          </button>
        </div>
      </div>

      {result && (
        <div style={{ background: "#1e293b", padding: "20px", borderRadius: "8px", border: result.congruent ? "1px solid #4ade80" : "1px solid #f87171" }}>
          {result.error ? (
            <div style={{ color: "#f87171" }}>Error: {result.error}</div>
          ) : (
            <>
              <h2 style={{ color: result.congruent ? "#4ade80" : "#f87171", marginTop: 0 }}>
                {result.congruent ? "✓ Sam Congruent" : "✗ Not Congruent"}
              </h2>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginTop: "15px" }}>
                <div><span style={{ color: "#64748b" }}>Total Matras:</span> {result.total_matras}</div>
                <div><span style={{ color: "#64748b" }}>Residue:</span> {result.residue}</div>
                <div><span style={{ color: "#64748b" }}>Target:</span> {result.target}</div>
                <div><span style={{ color: "#64748b" }}>Deviation:</span> {result.deviation}</div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
