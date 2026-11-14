import { useState, useRef, useEffect } from "react";
import { API_URL } from "./config";

// Load 22-sruti table on mount (frequencies for playback)
async function fetchSrutiTable() {
  const res = await fetch(`${API_URL}/api/v1/sruti?sa_hz=240`);
  const data = await res.json();
  return data.intervals || [];
}

export default function Studio3Tab() {
  // === Tala congruence verifier state ===
  const [pluta, setPluta] = useState(0);
  const [dirgha, setDirgha] = useState(0);
  const [cycle, setCycle] = useState(16);
  const [tStart, setTStart] = useState(0);
  const [laghu, setLaghu] = useState(0);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // === 22-sruti audio state ===
  const [srutiTable, setSrutiTable] = useState([]);
  const [audioReady, setAudioReady] = useState(false);
  const [nowPlaying, setNowPlaying] = useState(null); // index of sruti currently playing
  const [audioError, setAudioError] = useState(null);
  const audioCtxRef = useRef(null);
  const workletNodeRef = useRef(null);
  const workletLoadedRef = useRef(false);

  useEffect(() => {
    fetchSrutiTable().then((rows) => {
      setSrutiTable(rows);
      setAudioReady(rows.length > 0);
    });
  }, []);

  // Lazily initialize AudioContext + worklet on first user gesture
  const ensureAudio = async () => {
    if (workletNodeRef.current) return workletNodeRef.current;
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      await ctx.audioWorklet.addModule("/js/sruti-processor.js");
      const node = new AudioWorkletNode(ctx, "sruti-oscillator");
      node.connect(ctx.destination);
      audioCtxRef.current = ctx;
      workletNodeRef.current = node;
      workletLoadedRef.current = true;
      return node;
    } catch (e) {
      setAudioError(`Audio init failed: ${e.message}`);
      return null;
    }
  };

  const playSruti = async (entry, durationMs = 600) => {
    const node = await ensureAudio();
    if (!node) return;
    setNowPlaying(entry.index);
    node.port.postMessage({
      type: "play",
      freq: entry.frequency_hz,
      durationMs,
      gain: 0.15,
    });
    setTimeout(() => {
      setNowPlaying((cur) => (cur === entry.index ? null : cur));
    }, durationMs);
  };

  const playFullScale = async () => {
    const node = await ensureAudio();
    if (!node || srutiTable.length === 0) return;
    for (const entry of srutiTable) {
      setNowPlaying(entry.index);
      node.port.postMessage({
        type: "play",
        freq: entry.frequency_hz,
        durationMs: 550,
        gain: 0.15,
      });
      await new Promise((r) => setTimeout(r, 600));
    }
    setNowPlaying(null);
  };

  const stopAudio = () => {
    if (workletNodeRef.current) {
      workletNodeRef.current.port.postMessage({ type: "stop" });
    }
    setNowPlaying(null);
  };

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
      <h1 style={{ color: "#f472b6" }}>Studio III: Tāla & 22-Śruti</h1>
      <p style={{ color: "#94a3b8" }}>
        Verify the Diophantine invariant & hear the 22 microtonal intervals in Just Intonation
      </p>

      {/* ============= TALA CONGRUENCE VERIFIER ============= */}
      <h2 style={{ color: "#fbbf24", fontSize: "16px", marginTop: "20px" }}>Tāla Congruence Verifier</h2>
      <p style={{ color: "#64748b", fontSize: "13px" }}>3P + 2D + L + t_start ≡ 17 (mod C)</p>

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
        <div style={{ background: "#1e293b", padding: "15px", borderRadius: "8px", marginBottom: "20px", border: result.congruent ? "1px solid #4ade80" : "1px solid #f87171" }}>
          {result.error ? (
            <div style={{ color: "#f87171" }}>Error: {result.error}</div>
          ) : (
            <>
              <h3 style={{ color: result.congruent ? "#4ade80" : "#f87171", marginTop: 0, marginBottom: "8px" }}>
                {result.congruent ? "✓ Sam Congruent" : "✗ Not Congruent"}
              </h3>
              <div style={{ fontSize: "13px", color: "#94a3b8" }}>
                Total Matras: {result.total_matras} · Residue: {result.residue} · Target: {result.target} · Deviation: {result.deviation}
              </div>
            </>
          )}
        </div>
      )}

      {/* ============= 22-SRUTI PLAYER ============= */}
      <h2 style={{ color: "#38bdf8", fontSize: "16px", marginTop: "30px" }}>22-Śruti Just Intonation Player</h2>
      <p style={{ color: "#64748b", fontSize: "13px" }}>
        Sa = 240 Hz · all intervals derived from 5-limit Ahobala ratios · click any row to hear it
      </p>

      {audioError && (
        <div style={{ padding: "10px", background: "#7f1d1d", color: "#fca5a5", borderRadius: "4px", marginBottom: "10px", fontSize: "13px" }}>
          {audioError}
        </div>
      )}

      <div style={{ display: "flex", gap: "10px", marginBottom: "15px" }}>
        <button
          onClick={playFullScale}
          disabled={!audioReady}
          style={{ padding: "10px 20px", background: "#38bdf8", border: "none", borderRadius: "6px", fontWeight: "bold", cursor: audioReady ? "pointer" : "wait", color: "#0f172a" }}
        >
          ▶ Play Full 22-Śruti Scale
        </button>
        <button
          onClick={stopAudio}
          disabled={!audioReady}
          style={{ padding: "10px 20px", background: "#64748b", border: "none", borderRadius: "6px", fontWeight: "bold", cursor: audioReady ? "pointer" : "wait", color: "white" }}
        >
          ◼ Stop
        </button>
      </div>

      {srutiTable.length === 0 ? (
        <div style={{ color: "#64748b" }}>Loading śruti table...</div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr style={{ color: "#64748b", textAlign: "left", borderBottom: "1px solid #334155" }}>
              <th style={{ padding: "8px" }}>#</th>
              <th style={{ padding: "8px" }}>Name</th>
              <th style={{ padding: "8px" }}>Svara</th>
              <th style={{ padding: "8px" }}>Ratio</th>
              <th style={{ padding: "8px" }}>Hz</th>
              <th style={{ padding: "8px" }}>Cents</th>
              <th style={{ padding: "8px" }}>Play</th>
            </tr>
          </thead>
          <tbody>
            {srutiTable.map((row) => {
              const isPlaying = nowPlaying === row.index;
              return (
                <tr
                  key={row.index}
                  style={{
                    borderTop: "1px solid #1e293b",
                    background: isPlaying ? "#1e3a5f" : "transparent",
                  }}
                >
                  <td style={{ padding: "8px", color: "#64748b" }}>{row.index}</td>
                  <td style={{ padding: "8px" }}>{row.name}</td>
                  <td style={{ padding: "8px", color: "#f472b6" }}>{row.svara_symbol}</td>
                  <td style={{ padding: "8px", fontFamily: "monospace" }}>{row.ratio}</td>
                  <td style={{ padding: "8px", fontFamily: "monospace" }}>{row.frequency_hz.toFixed(2)}</td>
                  <td style={{ padding: "8px", fontFamily: "monospace", color: "#94a3b8" }}>{row.cents.toFixed(2)}</td>
                  <td style={{ padding: "8px" }}>
                    <button
                      onClick={() => playSruti(row, 600)}
                      disabled={!audioReady}
                      style={{
                        padding: "4px 12px",
                        background: isPlaying ? "#fbbf24" : "#334155",
                        border: "none",
                        borderRadius: "4px",
                        color: isPlaying ? "#0f172a" : "#e2e8f0",
                        fontWeight: "bold",
                        cursor: audioReady ? "pointer" : "wait",
                        fontSize: "12px",
                      }}
                    >
                      {isPlaying ? "▶" : "▶"}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}