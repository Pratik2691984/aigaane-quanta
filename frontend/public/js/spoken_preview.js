// Opt-in Spoken Sanskrit Preview using ninada (neural ONNX TTS).
// Modern spoken pronunciation preview ONLY — NOT Vedic svara/recension recitation
// and NOT 22-sruti / tala / MIDI synthesis.
// Lazy-loaded: bundle & ONNX weights are fetched only when requested by the user.

let ninadaModulePromise = null;

function resolveNinadaCallable(mod) {
  if (typeof mod === "function") return mod;
  if (mod && typeof mod.default === "function") return mod.default;
  if (mod && typeof mod.ninada === "function") return mod.ninada;

  if (mod && typeof mod === "object") {
    for (const [key, val] of Object.entries(mod)) {
      if (typeof val === "function" && /ninada|voice|tts|synth/i.test(key)) {
        return val;
      }
    }
  }

  if (typeof globalThis !== "undefined") {
    if (typeof globalThis.ninada === "function") return globalThis.ninada;
    if (typeof globalThis.__ninada === "function") return globalThis.__ninada;
  }

  return null;
}

async function getNinada(bundleUrl = "./vendor/ninada.bundle.mjs") {
  if (!ninadaModulePromise) {
    ninadaModulePromise = import(bundleUrl)
      .then((mod) => {
        const fn = resolveNinadaCallable(mod);
        if (!fn) {
          const keys = mod && typeof mod === "object" ? Object.keys(mod).join(", ") : typeof mod;
          throw new Error(`ninada bundle did not export a callable initializer (exports: ${keys || "none"})`);
        }
        return fn;
      })
      .catch((err) => {
        ninadaModulePromise = null;
        throw err;
      });
  }
  return ninadaModulePromise;
}

function encodeWavMono(samples, sampleRate = 24000) {
  const pcmLen = samples.length;
  const buffer = new ArrayBuffer(44 + pcmLen * 2);
  const view = new DataView(buffer);

  const writeAscii = (offset, str) => {
    for (let i = 0; i < str.length; i++) {
      view.setUint8(offset + i, str.charCodeAt(i));
    }
  };

  writeAscii(0, "RIFF");
  view.setUint32(4, 36 + pcmLen * 2, true);
  writeAscii(8, "WAVE");
  writeAscii(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeAscii(36, "data");
  view.setUint32(40, pcmLen * 2, true);

  let offset = 44;
  for (let i = 0; i < pcmLen; i++) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
    offset += 2;
  }

  return new Blob([buffer], { type: "audio/wav" });
}

export async function runSpokenSanskritPreview(text, options = {}) {
  const {
    voice = "sa",
    bundleUrl = "./vendor/ninada.bundle.mjs",
    signal,
    onStatus,
    onChunk,
  } = options;

  const modelKey = voice === "sa_female" || voice === "female" ? "sa_female" : "sa";
  const ninadaVoice = modelKey === "sa_female" ? "female" : "male";
  const modelUrl = `https://huggingface.co/gnumanth/ninada/resolve/main/onnx/${modelKey}.onnx`;

  onStatus?.("loading-runtime", "Preparing spoken Sanskrit preview module (lazy-loaded)...");
  const ninada = await getNinada(bundleUrl);
  if (signal?.aborted) {
    throw new DOMException("Aborted", "AbortError");
  }

  onStatus?.("loading-model", `Loading ${modelKey} neural weights (uses browser CacheStorage when warm)...`);
  const voiceInstance = await ninada("sanskrit", {
    lang: "sa",
    voice: ninadaVoice,
    models: { [modelKey]: modelUrl },
  });

  if (signal?.aborted) {
    throw new DOMException("Aborted", "AbortError");
  }

  const chunks = [];
  let firstChunkMs = null;
  let sampleRate = 24000;
  const startedAt = performance.now();

  if (typeof voiceInstance.stream === "function") {
    onStatus?.("streaming", `Streaming spoken Sanskrit preview (${modelKey})...`);
    let index = 0;
    for await (const chunk of voiceInstance.stream(text, { lang: "sa", voice: ninadaVoice })) {
      if (signal?.aborted) {
        throw new DOMException("Aborted", "AbortError");
      }
      const elapsedMs = performance.now() - startedAt;
      if (firstChunkMs === null) {
        firstChunkMs = typeof chunk?.ttfaMs === "number" ? chunk.ttfaMs : elapsedMs;
      }
      if (typeof chunk?.sampleRate === "number" && chunk.sampleRate > 0) {
        sampleRate = chunk.sampleRate;
      }
      const pcm = chunk?.pcm instanceof Float32Array ? chunk.pcm : null;
      if (pcm && pcm.length > 0) {
        chunks.push(pcm);
        onChunk?.({
          index,
          pcm,
          sampleRate,
          ttfaMs: firstChunkMs,
          elapsedMs,
        });
      }
      index++;
    }
  }

  const totalSamples = chunks.reduce((sum, arr) => sum + arr.length, 0);

  if (totalSamples === 0 && typeof voiceInstance.synthesize === "function") {
    onStatus?.("synthesizing", `Stream returned 0 samples for ${modelKey}; falling back to synthesize()...`);
    const res = await voiceInstance.synthesize(text, { lang: "sa", voice: ninadaVoice });
    if (res?.wav && res.wav.byteLength > 44) {
      const totalMs = performance.now() - startedAt;
      return {
        blob: new Blob([res.wav], { type: "audio/wav" }),
        ttfaMs: totalMs,
        totalMs,
        chunks: res.meta?.chunks ?? 1,
        tier: res.meta?.tier ?? "synthesize_fallback",
        modelKey,
      };
    }
  }

  if (totalSamples === 0) {
    throw new Error(`No vocal PCM samples returned for ${modelKey}`);
  }

  const merged = new Float32Array(totalSamples);
  let pos = 0;
  for (const arr of chunks) {
    merged.set(arr, pos);
    pos += arr.length;
  }

  const totalMs = performance.now() - startedAt;
  return {
    blob: encodeWavMono(merged, sampleRate),
    ttfaMs: firstChunkMs ?? totalMs,
    totalMs,
    chunks: chunks.length,
    tier: "neural_onnx_stream",
    modelKey,
  };
}