import { useState } from "react";
import { API_URL } from "./config";

const SAMPLES = [
  { label: "Gītā 1.1 (anuṣṭubh)",     value: "dharmakṣetre kurukṣetre samavetā yuyutsavaḥ" },
  { label: "Short junction",          value: "dharmakṣetre kurukṣetre" },
  { label: "Sandhi case",             value: "rāmeti" },
  { label: "Devanagari input",        value: "धर्मक्षेत्रे कुरुक्षेत्रे" },
];

const STAGE_ORDER = ["normalize", "sandhi", "morphology", "chandas", "sruti"];

function Card({ title, subtitle, accent, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div style={{
      background: "#1e293b", borderRadius: "10px", marginBottom: "14px",
      border: `1px solid ${accent || "#334155"}`, overflow: "hidden",
    }}>
      <div
        onClick={() => setOpen(!open)}
        style={{
          padding: "12px 16px", display: "flex", justifyContent: "space-between",
          alignItems: "center", cursor: "pointer",
          borderBottom: open ? "1px solid #334155" : "none",
        }}
      >
        <div>
          <div style={{ color: accent || "#a78bfa", fontWeight: "bold", fontSize: "15px" }}>{title}</div>
          {subtitle && <div style={{ color: "#64748b", fontSize: "12px", marginTop: "2px" }}>{subtitle}</div>}
        </div>
        <span style={{ color: "#64748b" }}>{open ? "▾" : "▸"}</span>
      </div>
      {open && <div style={{ padding: "16px" }}>{children}</div>}
    </div>
  );
}

export default function PipelineTab() {
  const [text, setText] = useState("dharmakṣetre kurukṣetre");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const run = async () => {
    const query = text.trim();
    if (!query) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API_URL}/api/v3/pipeline`, {
        method: "POST",
        headers: { "Content-Type": "application/json; charset=utf-8" },
        body: JSON.stringify({ text: query }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setResult(await res.json());
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  const chandas = result?.chandas;
  const chandasMeter = chandas?.meter;
  const stages = result?.stages || [];
  const stageMap = Object.fromEntries(stages.map(s => [s.name, s]));

  return (
    <div style={{ padding: "20px", color: "#e2e8f0", maxWidth: "1100px", margin: "0 auto" }}>
      <h1 style={{ color: "#38bdf8" }}>Deterministic Verse Pipeline</h1>
      <p style={{ color: "#94a3b8", marginBottom: "20px" }}>
        One call: normalize → tokenize → sandhi split → morphology → chandas → 22-śruti.
        Every stage sūtra-cited. No LLM.
      </p>

      <div style={{ marginBottom: "10px" }}>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={2}
          placeholder="Enter a Sanskrit verse (IAST, Devanagari, or SLP1)"
          style={{
            width: "100%", padding: "10px", borderRadius: "6px", fontSize: "15px",
            border: "1px solid #334155", background: "#1e293b", color: "white",
            fontFamily: "'Noto Serif', serif", resize: "vertical",
            boxSizing: "border-box",
          }}
        />
      </div>

      <div style={{ display: "flex", gap: "8px", marginBottom: "16px", flexWrap: "wrap", alignItems: "center" }}>
        <button
          onClick={run}
          disabled={loading}
          style={{
            padding: "10px 20px", background: "#38bdf8", border: "none",
            borderRadius: "6px", fontWeight: "bold", cursor: loading ? "wait" : "pointer",
            color: "#0f172a",
          }}
        >
          {loading ? "Analyzing…" : "Analyze"}
        </button>
        {SAMPLES.map((s) => (
          <button
            key={s.label}
            onClick={() => setText(s.value)}
            style={{
              padding: "6px 12px", background: "transparent", color: "#94a3b8",
              border: "1px solid #334155", borderRadius: "6px",
              fontSize: "12px", cursor: "pointer",
            }}
          >
            {s.label}
          </button>
        ))}
      </div>

      {error && (
        <div style={{
          padding: "12px", background: "#7f1d1d", color: "#fca5a5",
          borderRadius: "6px", marginBottom: "16px",
        }}>
          Error: {error}
        </div>
      )}

      {result && (
        <div>
          <Card title="1 · Normalize" subtitle={`detected: ${result.normalized?.detected || "—"}`} accent="#4ade80" defaultOpen={false}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
              <div style={{ padding: "10px", background: "#0f172a", borderRadius: "6px" }}>
                <div style={{ color: "#64748b", fontSize: "11px", marginBottom: "4px" }}>INPUT</div>
                <div style={{ fontFamily: "'Noto Serif', serif" }}>{result.normalized?.input || result.input}</div>
              </div>
              <div style={{ padding: "10px", background: "#0f172a", borderRadius: "6px" }}>
                <div style={{ color: "#64748b", fontSize: "11px", marginBottom: "4px" }}>IAST (canonical)</div>
                <div style={{ fontFamily: "'Noto Serif', serif" }}>{result.normalized?.iast || "—"}</div>
              </div>
            </div>
          </Card>

          <Card title={`2 · Tokens (${result.tokens?.length || 0})`} subtitle="sandhi splits, morphology, semantic" accent="#a78bfa">
            {result.tokens?.length === 0 && <div style={{ color: "#94a3b8" }}>No tokens.</div>}
            {(result.tokens || []).map((tok, i) => (
              <div key={i} style={{
                padding: "12px", background: "#0f172a", borderRadius: "6px",
                marginBottom: i < result.tokens.length - 1 ? "10px" : 0,
              }}>
                <div style={{ display: "flex", alignItems: "baseline", gap: "10px", marginBottom: "8px" }}>
                  <span style={{ color: "#38bdf8", fontSize: "18px", fontFamily: "'Noto Serif', serif" }}>{tok.surface}</span>
                  {tok.split_applied && (
                    <span style={{
                      padding: "2px 8px", background: "#1e1b4b", color: "#a78bfa",
                      fontSize: "11px", borderRadius: "4px", border: "1px solid #a78bfa",
                    }}>
                      split
                    </span>
                  )}
                </div>
                {tok.splits && tok.splits.length > 0 && (
                  <div style={{ marginBottom: "8px", paddingLeft: "10px", borderLeft: "2px solid #a78bfa" }}>
                    <div style={{ color: "#64748b", fontSize: "11px", marginBottom: "4px" }}>SANDHI SPLITS</div>
                    {tok.splits.map((s, j) => (
                      <div key={j} style={{ fontSize: "13px", color: "#94a3b8" }}>
                        {s.parts.join(" + ")} · {s.rule} · <span style={{ color: "#a78bfa" }}>{s.sutra}</span>
                      </div>
                    ))}
                  </div>
                )}
                {(tok.morphology || tok.semantic) && (
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginTop: "6px" }}>
                    {tok.morphology && (
                      <div style={{ padding: "8px", background: "#1e293b", borderRadius: "4px" }}>
                        <div style={{ color: "#64748b", fontSize: "11px", marginBottom: "2px" }}>MORPHOLOGY</div>
                        <div style={{ fontSize: "12px" }}>
                          {Object.entries(tok.morphology).slice(0, 4).map(([k, v]) =>
                            v != null && (
                              <div key={k} style={{ color: "#94a3b8" }}>
                                <span style={{ color: "#64748b" }}>{k}:</span> {String(v)}
                              </div>
                            )
                          )}
                        </div>
                      </div>
                    )}
                    {tok.semantic && (
                      <div style={{ padding: "8px", background: "#1e293b", borderRadius: "4px" }}>
                        <div style={{ color: "#64748b", fontSize: "11px", marginBottom: "2px" }}>SEMANTIC</div>
                        <div style={{ fontSize: "12px", color: "#94a3b8" }}>
                          {tok.semantic.dhatu && <div><span style={{ color: "#64748b" }}>√</span> {tok.semantic.dhatu}</div>}
                          {tok.semantic.gloss && <div>{tok.semantic.gloss}</div>}
                        </div>
                      </div>
                    )}
                  </div>
                )}
                {!tok.split_applied && !tok.morphology && !tok.semantic && (
                  <div style={{ color: "#64748b", fontSize: "12px", fontStyle: "italic" }}>
                    no sandhi junction · not in lexicon (atomic token)
                  </div>
                )}
              </div>
            ))}
          </Card>

          <Card
            title="3 · Chandas"
            subtitle={chandasMeter ? `${chandasMeter.meter} · ${chandas?.syllable_count} syllables · ${chandas?.matra_sum} mātrās` : "—"}
            accent="#fbbf24"
          >
            {chandas ? (
              <>
                <div style={{ marginBottom: "12px", display: "flex", gap: "6px", flexWrap: "wrap" }}>
                  {(chandas.weights || []).map((w, i) => (
                    <span key={i} style={{
                      padding: "6px 12px", borderRadius: "4px",
                      background: w === "G" ? "#7c2d12" : "#1e3a8a",
                      color: w === "G" ? "#fbbf24" : "#93c5fd",
                      fontSize: "13px", fontWeight: "bold", fontFamily: "monospace",
                    }}>
                      {w}
                    </span>
                  ))}
                </div>
                {chandasMeter && (
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
                    <div style={{ padding: "8px", background: "#0f172a", borderRadius: "4px" }}>
                      <div style={{ color: "#64748b", fontSize: "11px" }}>METER</div>
                      <div style={{ color: "#fbbf24", fontWeight: "bold" }}>{chandasMeter.meter}</div>
                    </div>
                    <div style={{ padding: "8px", background: "#0f172a", borderRadius: "4px" }}>
                      <div style={{ color: "#64748b", fontSize: "11px" }}>MATCH TYPE</div>
                      <div>{chandasMeter.match_type || "—"}</div>
                    </div>
                  </div>
                )}
              </>
            ) : <div style={{ color: "#94a3b8" }}>Chandas stage did not return data.</div>}
          </Card>

          <Card
            title={`4 · 22-Śruti Map (${result.sruti_map?.length || 0})`}
            subtitle="syllable → 5-limit JI interval"
            accent="#f472b6"
            defaultOpen={false}
          >
            {result.sruti_map?.length > 0 ? (
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
                <thead>
                  <tr style={{ color: "#64748b", textAlign: "left", borderBottom: "1px solid #334155" }}>
                    <th style={{ padding: "6px" }}>#</th>
                    <th style={{ padding: "6px" }}>Weight</th>
                    <th style={{ padding: "6px" }}>Name</th>
                    <th style={{ padding: "6px" }}>Svara</th>
                    <th style={{ padding: "6px" }}>Ratio</th>
                    <th style={{ padding: "6px" }}>Hz</th>
                  </tr>
                </thead>
                <tbody>
                  {result.sruti_map.map((s, i) => (
                    <tr key={i} style={{ borderTop: "1px solid #0f172a" }}>
                      <td style={{ padding: "6px", color: "#64748b" }}>{s.index}</td>
                      <td style={{ padding: "6px" }}>
                        <span style={{ color: s.weight === "G" ? "#fbbf24" : "#93c5fd" }}>{s.weight}</span>
                      </td>
                      <td style={{ padding: "6px" }}>{s.name}</td>
                      <td style={{ padding: "6px", color: "#f472b6" }}>{s.svara}</td>
                      <td style={{ padding: "6px", fontFamily: "monospace" }}>{s.ratio}</td>
                      <td style={{ padding: "6px", fontFamily: "monospace" }}>{s.hz?.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : <div style={{ color: "#94a3b8" }}>No śruti mapping.</div>}
          </Card>

          <Card
            title="5 · Stage Timing"
            subtitle={stages.map(s => `${s.name}=${s.ok ? "ok" : "fail"}`).join(" · ")}
            accent="#4ade80"
            defaultOpen={false}
          >
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "8px" }}>
              {STAGE_ORDER.map((name) => {
                const s = stageMap[name];
                const ok = s?.ok;
                return (
                  <div key={name} style={{
                    padding: "10px", background: "#0f172a", borderRadius: "6px",
                    border: `1px solid ${ok ? "#4ade80" : "#f87171"}`,
                  }}>
                    <div style={{ color: "#64748b", fontSize: "11px" }}>{name}</div>
                    <div style={{ color: ok ? "#4ade80" : "#f87171", fontWeight: "bold" }}>
                      {ok ? "✓" : "✗"} {s?.ms?.toFixed(1) || "—"} ms
                    </div>
                    {s?.error && <div style={{ color: "#fca5a5", fontSize: "11px", marginTop: "4px" }}>{s.error}</div>}
                  </div>
                );
              })}
            </div>
            {result.warnings?.length > 0 && (
              <div style={{ marginTop: "12px", padding: "8px", background: "#7f1d1d", borderRadius: "4px" }}>
                <div style={{ color: "#fca5a5", fontSize: "12px", marginBottom: "4px" }}>WARNINGS</div>
                {result.warnings.map((w, i) => (
                  <div key={i} style={{ color: "#fecaca", fontSize: "12px" }}>• {w}</div>
                ))}
              </div>
            )}
          </Card>
        </div>
      )}
    </div>
  );
}