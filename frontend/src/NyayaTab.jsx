import { useState } from "react";

export default function NyayaTab() {
  const [candidateId, setCandidateId] = useState("cand_01");
  const [sutraChain, setSutraChain] = useState("1.1.1, 1.1.2");
  const [proof, setProof] = useState(null);
  const [loading, setLoading] = useState(false);

  const verify = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v3/nyaya/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json; charset=utf-8" },
        body: JSON.stringify({
          candidate_id: candidateId,
          sutra_chain: sutraChain.split(",").map((s) => s.trim()).filter(Boolean),
        }),
      });
      setProof(await res.json());
    } catch (e) {
      setProof({ error: String(e) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", color: "#e2e8f0" }}>
      <h1 style={{ color: "#fbbf24" }}>Nyāya Syllogistic Verifier</h1>
      <p style={{ color: "#94a3b8" }}>5-step formal proof validation (pratijñā → nigamana)</p>

      <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
        <input
          value={candidateId}
          onChange={(e) => setCandidateId(e.target.value)}
          placeholder="Candidate ID"
          style={{
            padding: "10px", width: "150px", borderRadius: "6px",
            border: "1px solid #334155", background: "#1e293b", color: "white",
          }}
        />
        <input
          value={sutraChain}
          onChange={(e) => setSutraChain(e.target.value)}
          placeholder="Sutra chain (comma-separated)"
          style={{
            padding: "10px", flex: 1, borderRadius: "6px",
            border: "1px solid #334155", background: "#1e293b", color: "white",
          }}
        />
        <button
          onClick={verify}
          disabled={loading}
          style={{
            padding: "10px 20px", background: "#fbbf24", border: "none",
            borderRadius: "6px", fontWeight: "bold", cursor: "pointer",
          }}
        >
          {loading ? "Verifying..." : "Verify"}
        </button>
      </div>

      {proof && (
        <div style={{
          background: "#1e293b", padding: "20px", borderRadius: "10px",
          border: proof.is_valid ? "1px solid #4ade80" : "1px solid #f87171",
        }}>
          {proof.error ? (
            <div style={{ color: "#f87171" }}>Error: {proof.error}</div>
          ) : (
            <>
              <h2 style={{ color: proof.is_valid ? "#4ade80" : "#f87171" }}>
                {proof.is_valid ? "✓ Proof Valid" : "✗ Proof Invalid"}
              </h2>

              {[
                ["1. Pratijñā (Proposition)", proof.pratijna],
                ["2. Hetu (Reason)", proof.hetu],
                ["3. Udāharaṇa (Example)", proof.udaharana],
                ["4. Upanaya (Application)", proof.upanaya],
                ["5. Nigamana (Conclusion)", proof.nigamana],
              ].map(([label, value]) => (
                <div key={label} style={{
                  padding: "12px", background: "#0f172a",
                  borderRadius: "8px", marginBottom: "8px",
                }}>
                  <div style={{ color: "#94a3b8", fontSize: "12px" }}>{label}</div>
                  <div style={{ color: "#e2e8f0", marginTop: "4px" }}>{value}</div>
                </div>
              ))}

              {proof.validation_notes?.length > 0 && (
                <div style={{ marginTop: "10px", color: "#fbbf24" }}>
                  <strong>Notes:</strong>
                  <ul>{proof.validation_notes.map((n, i) => <li key={i}>{n}</li>)}</ul>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}