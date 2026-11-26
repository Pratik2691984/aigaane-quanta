import { useState, useRef, useEffect } from "react";
import { API_URL } from "./config";
import VedicPanel from "./VedicPanel";

// Load 22-sruti table on mount (frequencies for playback)
async function fetchSrutiTable() {
  const res = await fetch(`${API_URL}/api/v1/sruti?sa_hz=240`);
  const data = await res.json();
  return data.intervals || [];
}

export default function Studio3Tab() {
  // === Pingala gana scansion state ===
  const [ganaText, setGanaText] = useState("dharmakṣetre kurukṣetre");
  const [ganaLoading, setGanaLoading] = useState(false);
  const [ganaResult, setGanaResult] = useState(null);

  // === Tihai congruence verifier state ===
  const [tihaiPhrase, setTihaiPhrase] = useState("5");
  const [tihaiGap, setTihaiGap] = useState("1");
  const [tihaiCycle, setTihaiCycle] = useState("16");
  const [tihaiStart, setTihaiStart] = useState("0");
  const [tihaiAnchor, setTihaiAnchor] = useState("17");
  const [tihaiLoading, setTihaiLoading] = useState(false);
  const [tihaiResult, setTihaiResult] = useState(null);

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
  const [tanpuraOn, setTanpuraOn] = useState(false);
  const [tanpuraGain, setTanpuraGain] = useState(0.08);
  const [andolanOn, setAndolanOn] = useState(false);
  const [andolanHz, setAndolanHz] = useState(2.5);
  const [andolanDepthCents, setAndolanDepthCents] = useState(12);
  const audioCtxRef = useRef(null);
  const workletNodeRef = useRef(null);
  const workletLoadedRef = useRef(false);

  // Tala rhythm player state
  const [talaList, setTalaList] = useState([]);
  const [selectedTala, setSelectedTala] = useState("");
  const [bpm, setBpm] = useState(60);
  const [talaPlaying, setTalaPlaying] = useState(false);
  const talaPlayingRef = useRef(false);
  const [currentAkshara, setCurrentAkshara] = useState(0);
  const talaTimeoutsRef = useRef([]);

  const setTalaPlayingSync = (val) => {
    talaPlayingRef.current = val;
    setTalaPlaying(val);
  };

  // === Vedic Chant state ===
  const [vedicText, setVedicText] = useState("");
  const [vedicRecension, setVedicRecension] = useState("rgveda_sakala");
  const [vedicLoading, setVedicLoading] = useState(false);
  const [vedicPlaying, setVedicPlaying] = useState(false);
  const [vedicNotice, setVedicNotice] = useState(null);
  const [vedicAlign, setVedicAlign] = useState(false);
  const [vedicTala, setVedicTala] = useState("");
  const [vedicDownloading, setVedicDownloading] = useState(false);
  const [vedicRenderInfo, setVedicRenderInfo] = useState(null);
  const [vedicDrone, setVedicDrone] = useState(true);

  useEffect(() => {
    if (vedicAlign && !vedicTala && talaList.length > 0) {
      setVedicTala(talaList[0].name);
    }
  }, [vedicAlign, vedicTala, talaList]);

  useEffect(() => {
    fetchSrutiTable().then((rows) => {
      setSrutiTable(rows);
      setAudioReady(rows.length > 0);
    });
  }, []);

  useEffect(() => {
    fetch(`${API_URL}/api/v3/studio3/tala/list`)
      .then((r) => r.json())
      .then((data) => {
        const talas = data.talas || [];
        setTalaList(talas);
        if (talas.length > 0) setSelectedTala(talas[0].name);
      })
      .catch((e) => console.warn("Tala list fetch failed:", e));
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
      andolanHz: andolanOn ? andolanHz : 0,
      andolanDepthCents: andolanOn ? andolanDepthCents : 0,
      andolanAmpDepth: andolanOn ? 0.08 : 0,
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
        andolanHz: andolanOn ? andolanHz : 0,
        andolanDepthCents: andolanOn ? andolanDepthCents : 0,
        andolanAmpDepth: andolanOn ? 0.08 : 0,
      });
      await new Promise((r) => setTimeout(r, 600));
    }
    setNowPlaying(null);
  };

  
  const startTanpura = async () => {
    const node = await ensureAudio();
    if (!node) return;
    node.port.postMessage({
      type: "startDrone",
      saHz: 240,
      gain: tanpuraGain,
    });
    setTanpuraOn(true);
  };

  const stopTanpura = () => {
    if (workletNodeRef.current) {
      workletNodeRef.current.port.postMessage({ type: "stopDrone" });
    }
    setTanpuraOn(false);
  };

  const updateTanpuraGain = (g) => {
    setTanpuraGain(g);
    if (workletNodeRef.current && tanpuraOn) {
      workletNodeRef.current.port.postMessage({
        type: "setDroneGain",
        saHz: 240,
        gain: g,
      });
    }
  };

  const stopAudio = () => {
    if (workletNodeRef.current) {
      workletNodeRef.current.port.postMessage({ type: "stop" });
    }
    setNowPlaying(null);
  };

  const stopTala = () => {
    talaPlayingRef.current = false;
    talaTimeoutsRef.current.forEach((t) => clearTimeout(t));
    talaTimeoutsRef.current = [];
    setTalaPlaying(false);
    setCurrentAkshara(0);
    if (workletNodeRef.current) {
      workletNodeRef.current.port.postMessage({ type: "stop" });
    }
  };

  const stopVedicChant = () => {
    talaTimeoutsRef.current.forEach((t) => clearTimeout(t));
    talaTimeoutsRef.current = [];
    if (workletNodeRef.current) {
      workletNodeRef.current.port.postMessage({ type: "stop" });
    }
    setVedicPlaying(false);
  };

  const downloadVedicWav = async () => {
    if (!vedicText.trim()) return;
    setVedicDownloading(true);
    setVedicNotice(null);
    setVedicRenderInfo(null);
    try {
      const body = {
        text: vedicText,
        recension: vedicRecension,
        bpm: bpm,
        sa_hz: 240,
        drone_on: vedicDrone,
        sample_rate: 22050,
      };
      if (vedicAlign && vedicTala) {
        body.tala_name = vedicTala;
      }
      const res = await fetch(`${API_URL}/api/v3/vedic/render`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (data.rejected && data.rejected.length > 0) {
        setVedicNotice(data.rejected[0]);
        return;
      }
      if (!data.candidates || data.candidates.length === 0) {
        setVedicNotice({ reason_code: "EMPTY_INPUT", detail: "No render returned" });
        return;
      }
      const cand = data.candidates[0];
      const bin = atob(cand.wav_b64);
      const bytes = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      const blob = new Blob([bytes], { type: "audio/wav" });
      const url = URL.createObjectURL(blob);
      const sha8 = cand.sha256.slice(0, 8);
      const fname = `aigaane_vedic_${vedicRecension}_${sha8}.wav`;
      const a = document.createElement("a");
      a.href = url;
      a.download = fname;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setVedicRenderInfo({
        sha256: cand.sha256,
        duration_sec: cand.duration_sec,
        peak_db: cand.peak_db,
        rms_db: cand.rms_db,
        n_samples: cand.n_samples,
        filename: fname,
      });
    } catch (err) {
      setVedicNotice({ reason_code: "FETCH_ERROR", detail: String(err) });
    } finally {
      setVedicDownloading(false);
    }
  };

  const playVedicChant = async () => {
    if (!vedicText.trim()) return;
    const node = await ensureAudio();
    if (!node) return;
    setVedicLoading(true);
    setVedicNotice(null);
    stopVedicChant();

    try {
      let url = `${API_URL}/api/v3/vedic/contour`;
      let body = { text: vedicText, recension: vedicRecension, sa_hz: 240 };
      if (vedicAlign) {
        url = `${API_URL}/api/v3/vedic/align`;
        body = {
          text: vedicText,
          recension: vedicRecension,
          tala_name: vedicTala,
          bpm: bpm,
          sa_hz: 240,
        };
      }
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (data.rejected && data.rejected.length > 0) {
        setVedicNotice(data.rejected[0]);
        return;
      }
      if (!data.candidates || data.candidates.length === 0) {
        setVedicNotice({ reason_code: "EMPTY_INPUT", detail: "No contour returned" });
        return;
      }
      const cand = data.candidates[0];
      const saHz = 240;

      if (vedicAlign && cand.rhythm_events) {
        const rhythm = cand.rhythm_events;
        const totalSec = cand.tala_meta ? cand.tala_meta.total_sec : 0;
        rhythm.forEach((ev) => {
          const delayMs = ev.onset_sec * 1000;
          const durMs = ev.duration_sec * 1000;
          const startFreq = ev.start_ratio * saHz;
          const endFreq = ev.end_ratio * saHz;
          const kampaHz = ev.kampa ? ev.kampa.hz : 0;
          const kampaDepthCents = ev.kampa ? ev.kampa.depth_cents : 0;
          const gain = ev.sam_accent ? 0.22 : 0.15;
          const tid = setTimeout(() => {
            if (!workletNodeRef.current) return;
            workletNodeRef.current.port.postMessage({
              type: "play",
              freq: startFreq,
              endFreq: endFreq,
              durationMs: durMs,
              gain: gain,
              kampaHz: kampaHz,
              kampaDepthCents: kampaDepthCents,
            });
          }, delayMs);
          talaTimeoutsRef.current.push(tid);
        });
        setVedicPlaying(true);
        const stopTid = setTimeout(() => {
          setVedicPlaying(false);
          if (workletNodeRef.current) {
            workletNodeRef.current.port.postMessage({ type: "stop" });
          }
        }, totalSec * 1000 + 200);
        talaTimeoutsRef.current.push(stopTid);
      } else {
        const events = cand.contour_events;
        const beatSec = 60 / Math.max(30, bpm);
        let cumul = 0;
        events.forEach((ev) => {
          const delayMs = cumul * 1000;
          const durMs = ev.matra_duration * beatSec * 1000;
          const startFreq = ev.pitch.start_ratio * saHz;
          const endFreq = ev.pitch.end_ratio * saHz;
          const kampaHz = ev.pitch.kampa ? ev.pitch.kampa.hz : 0;
          const kampaDepthCents = ev.pitch.kampa ? ev.pitch.kampa.depth_cents : 0;
          const tid = setTimeout(() => {
            if (!workletNodeRef.current) return;
            workletNodeRef.current.port.postMessage({
              type: "play",
              freq: startFreq,
              endFreq: endFreq,
              durationMs: durMs,
              gain: 0.15,
              kampaHz: kampaHz,
              kampaDepthCents: kampaDepthCents,
            });
          }, delayMs);
          talaTimeoutsRef.current.push(tid);
          cumul += ev.matra_duration * beatSec;
        });
        setVedicPlaying(true);
        const stopTid = setTimeout(() => {
          setVedicPlaying(false);
          if (workletNodeRef.current) {
            workletNodeRef.current.port.postMessage({ type: "stop" });
          }
        }, cumul * 1000 + 200);
        talaTimeoutsRef.current.push(stopTid);
      }
    } catch (err) {
      setVedicNotice({ reason_code: "FETCH_ERROR", detail: String(err) });
    } finally {
      setVedicLoading(false);
    }
  };

  const playTala = async () => {
    const node = await ensureAudio();
    if (!node || !selectedTala) return;

    const tala = talaList.find((t) => t.name === selectedTala);
    if (!tala) return;

    stopTala();
    setTalaPlayingSync(true);

    const cycleLength = tala.cycle_length;
    const matraMs = (60 / bpm) * 1000;
    const totalCycleMs = cycleLength * matraMs;

    const scheduleCycle = () => {
      if (!talaPlayingRef.current) return;
      for (let i = 0; i < cycleLength; i++) {
        const isSam = i === 0;
        const freq = isSam ? 360.0 : 240.0;
        const gain = isSam ? 0.22 : 0.10;
        const delayMs = i * matraMs;

        const t = setTimeout(() => {
          if (!talaPlayingRef.current) return;
          setCurrentAkshara(i + 1);
          if (workletNodeRef.current) {
            workletNodeRef.current.port.postMessage({ type: "stop" });
            setTimeout(() => {
              if (!talaPlayingRef.current) return;
              if (workletNodeRef.current) {
                workletNodeRef.current.port.postMessage({
                  type: "play",
                  freq,
                  durationMs: Math.min(matraMs * 0.6, 400),
                  gain,
                });
              }
            }, 5);
          }
        }, delayMs);
        talaTimeoutsRef.current.push(t);
      }

      const loopTimeout = setTimeout(() => {
        if (talaPlayingRef.current) scheduleCycle();
      }, totalCycleMs);
      talaTimeoutsRef.current.push(loopTimeout);
    };

    scheduleCycle();
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

  const scanGanas = async () => {
    if (!ganaText.trim()) return;
    setGanaLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/chandas/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: ganaText.trim() }),
      });
      setGanaResult(await res.json());
    } catch (e) {
      setGanaResult({ errors: String(e) });
    } finally {
      setGanaLoading(false);
    }
  };

  const verifyTihai = async () => {
    setTihaiLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v3/studio3/tala/tihai`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phrase_matras: parseInt(tihaiPhrase, 10) || 0,
          gap_matras: parseInt(tihaiGap, 10) || 0,
          cycle_length: parseInt(tihaiCycle, 10) || 16,
          t_start: parseInt(tihaiStart, 10) || 0,
          sam_anchor: parseInt(tihaiAnchor, 10) || 17,
        }),
      });
      setTihaiResult(await res.json());
    } catch (e) {
      setTihaiResult({ error: String(e) });
    } finally {
      setTihaiLoading(false);
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

      {/* ============= PINGALA GANA SCANSION ============= */}
      <h2 style={{ color: "#38bdf8", fontSize: "16px", marginTop: "24px" }}>Piṅgala Gaṇa Vector Scansion</h2>
      <p style={{ color: "#64748b", fontSize: "13px" }}>
        3-syllable L/G binary vectors (L=0, G=1) via /api/v1/chandas/scan
      </p>

      <div style={{ display: "flex", gap: "10px", marginBottom: "14px" }}>
        <input
          type="text"
          value={ganaText}
          onChange={(e) => setGanaText(e.target.value)}
          placeholder="Enter IAST or Devanagari verse..."
          style={{ flex: 1, padding: "8px", background: "#1e293b", color: "white", border: "1px solid #334155", borderRadius: "4px" }}
        />
        <button
          onClick={scanGanas}
          disabled={ganaLoading}
          style={{ padding: "8px 16px", background: "#38bdf8", color: "#0f172a", border: "none", borderRadius: "4px", fontWeight: "bold", cursor: "pointer" }}
        >
          {ganaLoading ? "Scanning..." : "Scan Gaṇas"}
        </button>
      </div>

      {ganaResult && (
        <div style={{ background: "#1e293b", padding: "14px", borderRadius: "8px", marginBottom: "20px", border: "1px solid #334155" }}>
          {ganaResult.errors ? (
            <div style={{ color: "#f87171" }}>Error: {ganaResult.errors}</div>
          ) : (
            <>
              <div style={{ fontSize: "13px", color: "#94a3b8", marginBottom: "8px" }}>
                Pattern: <strong style={{ color: "#e2e8f0" }}>{ganaResult.pattern || "-"}</strong> · Syllables: {ganaResult.syllable_count ?? 0} · Mātrā Sum: {ganaResult.matra_sum ?? 0} · Binary: <strong style={{ color: "#38bdf8" }}>{ganaResult.ganas?.binary_string || ""}</strong>
                {ganaResult.ganas?.remainder_bits ? ` · Remainder: ${ganaResult.ganas.remainder_bits}` : ""}
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                {(ganaResult.ganas?.ganas || []).map((g) => (
                  <div key={g.index} style={{ background: "#0f172a", padding: "6px 10px", borderRadius: "6px", border: "1px solid #1e293b", fontSize: "12px" }}>
                    <span style={{ color: "#fbbf24", fontWeight: "bold" }}>{g.gana}</span>{" "}
                    <span style={{ color: "#94a3b8" }}>({g.bits} · {g.matras}m)</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* ============= TIHAI CONGRUENCE VERIFIER ============= */}
      <h2 style={{ color: "#fbbf24", fontSize: "16px", marginTop: "24px" }}>Tihāī Congruence Verifier</h2>
      <p style={{ color: "#64748b", fontSize: "13px" }}>
        3 × phrase_matras + 2 × gap_matras + t_start ≡ sam_anchor (mod cycle_length)
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "10px", marginBottom: "16px" }}>
        <div>
          <label style={{ display: "block", fontSize: "12px", color: "#94a3b8" }}>Phrase Mātrās (M)</label>
          <input type="number" value={tihaiPhrase} onChange={(e) => setTihaiPhrase(e.target.value)} style={{ width: "100%", padding: "8px", background: "#1e293b", color: "white", border: "1px solid #334155", borderRadius: "4px" }} />
        </div>
        <div>
          <label style={{ display: "block", fontSize: "12px", color: "#94a3b8" }}>Inter-Phrase Gap (G)</label>
          <input type="number" value={tihaiGap} onChange={(e) => setTihaiGap(e.target.value)} style={{ width: "100%", padding: "8px", background: "#1e293b", color: "white", border: "1px solid #334155", borderRadius: "4px" }} />
        </div>
        <div>
          <label style={{ display: "block", fontSize: "12px", color: "#94a3b8" }}>Cycle Length (C)</label>
          <input type="number" value={tihaiCycle} onChange={(e) => setTihaiCycle(e.target.value)} style={{ width: "100%", padding: "8px", background: "#1e293b", color: "white", border: "1px solid #334155", borderRadius: "4px" }} />
        </div>
        <div>
          <label style={{ display: "block", fontSize: "12px", color: "#94a3b8" }}>Start Offset (t_start)</label>
          <input type="number" value={tihaiStart} onChange={(e) => setTihaiStart(e.target.value)} style={{ width: "100%", padding: "8px", background: "#1e293b", color: "white", border: "1px solid #334155", borderRadius: "4px" }} />
        </div>
        <div>
          <label style={{ display: "block", fontSize: "12px", color: "#94a3b8" }}>Sam Anchor</label>
          <input type="number" value={tihaiAnchor} onChange={(e) => setTihaiAnchor(e.target.value)} style={{ width: "100%", padding: "8px", background: "#1e293b", color: "white", border: "1px solid #334155", borderRadius: "4px" }} />
        </div>
        <div style={{ display: "flex", alignItems: "flex-end" }}>
          <button onClick={verifyTihai} disabled={tihaiLoading} style={{ width: "100%", padding: "8px", background: "#fbbf24", color: "#0f172a", border: "none", borderRadius: "4px", fontWeight: "bold", cursor: "pointer" }}>
            {tihaiLoading ? "Checking..." : "Verify Tihāī"}
          </button>
        </div>
      </div>

      {tihaiResult && (
        <div style={{ background: "#1e293b", padding: "15px", borderRadius: "8px", marginBottom: "20px", border: tihaiResult.congruent ? "1px solid #4ade80" : "1px solid #f87171" }}>
          {tihaiResult.error ? (
            <div style={{ color: "#f87171" }}>Error: {tihaiResult.error}</div>
          ) : (
            <>
              <h3 style={{ color: tihaiResult.congruent ? "#4ade80" : "#f87171", marginTop: 0, marginBottom: "8px" }}>
                {tihaiResult.congruent ? "✓ Tihāī Sam Congruent" : "✗ Tihāī Not Congruent"}
              </h3>
              <div style={{ fontSize: "13px", color: "#94a3b8" }}>
                Tihāī Span: {tihaiResult.tihai_span_matras} · Total Mātrās: {tihaiResult.total_matras} · Residue: {tihaiResult.residue} · Target: {tihaiResult.target} · Deviation: {tihaiResult.deviation}
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


      <div style={{ display: "flex", gap: "12px", alignItems: "center", marginBottom: "12px", flexWrap: "wrap" }}>
        <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", color: "#94a3b8" }}>
          <input
            type="checkbox"
            checked={tanpuraOn}
            onChange={(e) => (e.target.checked ? startTanpura() : stopTanpura())}
            disabled={!audioReady}
          />
          Tanpura Drone (multi-harmonic)
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", color: "#94a3b8" }}>
          Level
          <input
            type="range"
            min="0"
            max="0.2"
            step="0.01"
            value={tanpuraGain}
            onChange={(e) => updateTanpuraGain(parseFloat(e.target.value))}
            disabled={!audioReady}
            style={{ width: "120px" }}
          />
          <span style={{ fontFamily: "monospace", color: "#64748b" }}>{tanpuraGain.toFixed(2)}</span>
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", color: "#94a3b8" }}>
          <input
            type="checkbox"
            checked={andolanOn}
            onChange={(e) => setAndolanOn(e.target.checked)}
            disabled={!audioReady}
          />
          Āndolan LFO
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", color: "#94a3b8" }}>
          Depth (¢)
          <input
            type="range"
            min="2"
            max="30"
            step="1"
            value={andolanDepthCents}
            onChange={(e) => setAndolanDepthCents(parseInt(e.target.value, 10))}
            disabled={!audioReady || !andolanOn}
            style={{ width: "100px" }}
          />
          <span style={{ fontFamily: "monospace", color: "#64748b" }}>
            {andolanDepthCents}¢ · {andolanHz.toFixed(1)}Hz
          </span>
        </label>
      </div>

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

      <h2 style={{ color: "#a78bfa", fontSize: "16px", marginTop: "40px" }}>Tala Rhythm Player</h2>
      <p style={{ color: "#64748b", fontSize: "13px" }}>
        Ticks on each akshara at the cycle length, accent on sam (akshara 1)
      </p>

      <div style={{ display: "flex", gap: "10px", alignItems: "flex-end", marginBottom: "15px", flexWrap: "wrap" }}>
        <div>
          <label style={{ display: "block", fontSize: "12px", color: "#94a3b8", marginBottom: "4px" }}>Tala</label>
          <select
            value={selectedTala}
            onChange={(e) => { stopTala(); setSelectedTala(e.target.value); }}
            style={{ padding: "8px", background: "#1e293b", color: "#e2e8f0", border: "1px solid #334155", borderRadius: "4px", minWidth: "220px" }}
          >
            {talaList.length === 0 && <option>Loading...</option>}
            {talaList.map((t) => (
              <option key={t.name} value={t.name}>
                {t.name} - {t.cycle_length} aksharas
              </option>
            ))}
          </select>
        </div>
        <div>
          <label style={{ display: "block", fontSize: "12px", color: "#94a3b8", marginBottom: "4px" }}>BPM</label>
          <input
            type="number"
            min={30}
            max={240}
            value={bpm}
            onChange={(e) => { stopTala(); setBpm(parseInt(e.target.value) || 60); }}
            style={{ width: "80px", padding: "8px", background: "#1e293b", color: "#e2e8f0", border: "1px solid #334155", borderRadius: "4px" }}
          />
        </div>
        <button
          onClick={talaPlaying ? stopTala : playTala}
          disabled={!audioReady || talaList.length === 0}
          style={{ padding: "10px 20px", background: talaPlaying ? "#64748b" : "#a78bfa", border: "none", borderRadius: "6px", fontWeight: "bold", cursor: audioReady ? "pointer" : "wait", color: "white" }}
        >
          {talaPlaying ? "Stop" : "Play Tala"}
        </button>
      </div>

      <VedicPanel
        text={vedicText}
        setText={setVedicText}
        recension={vedicRecension}
        setRecension={setVedicRecension}
        loading={vedicLoading}
        playing={vedicPlaying}
        notice={vedicNotice}
        onPlay={playVedicChant}
        onStop={stopVedicChant}
        align={vedicAlign}
        setAlign={setVedicAlign}
        talaList={talaList}
        tala={vedicTala}
        setTala={setVedicTala}
        bpm={bpm}
        onDownload={downloadVedicWav}
        downloading={vedicDownloading}
        renderInfo={vedicRenderInfo}
        drone={vedicDrone}
        setDrone={setVedicDrone}
      />

      {talaPlaying && selectedTala && (
        <div style={{ padding: "12px", background: "#0f172a", borderRadius: "6px", display: "flex", gap: "8px", flexWrap: "wrap" }}>
          {Array.from({ length: (talaList.find((t) => t.name === selectedTala) || {}).cycle_length || 0 }).map((_, i) => (
            <div
              key={i}
              style={{
                width: "32px", height: "32px",
                display: "flex", alignItems: "center", justifyContent: "center",
                background: currentAkshara === i + 1 ? "#fbbf24" : (i === 0 ? "#7c2d12" : "#334155"),
                color: currentAkshara === i + 1 ? "#0f172a" : "#e2e8f0",
                borderRadius: "4px", fontWeight: "bold", fontSize: "12px",
              }}
            >
              {i + 1}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}