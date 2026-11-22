# Aigaane-Quanta Architecture & Audio Boundaries

## Three-Tier Audio & Synthesis Boundaries

Aigaane separates deterministic Vedic recitation, deterministic musical/rhythmic synthesis, and opt-in modern neural spoken pronunciation into distinct layers so they are never conflated in code, UI, or recension handling:

### Tier 1 — Deterministic Vedic Recitation (Mode 1)
- **Role:** Deterministic Vedic recitation / accent (*svara*) and recension rendering.
- **Guardrails:** Fail closed on Sāmaveda variants (`samaveda`, `samaveda_*`) and unverified/unsupported recensions rather than silently falling back to a default recension such as `rgveda_sakala`.

### Tier 2 — Deterministic Musical, Śruti, Tāla, Japa & MIDI Synthesis
- **Role:** Deterministic musical pitch/tuning (including 22-śruti / just-intonation intervals, *rāga*, *tāla*, drone, Japa loops, and MIDI synthesis).
- **Guardrails:** Musical tuning and rhythmic/drone synthesis are distinct from Vedic *svara* accent rules and modern spoken prose pronunciation.

### Tier 3 — Opt-In Neural Spoken Sanskrit Preview (`ninada`)
- **Implementation:** `frontend/public/js/spoken_preview.js` dynamically importing `./vendor/ninada.bundle.mjs` (built into `frontend/public/js/vendor/` via `frontend/scripts/build-vendor.mjs` during `npm run build`).
- **Scope & Labeling:** Modern spoken Sanskrit pronunciation preview only—explicitly labeled in the UI as distinct from Vedic *svara* recitations and from 22-śruti / *tāla* / MIDI synthesis.
- **Lazy Loading & Artifact Hygiene:**
  - Never load `ninada` or fetch `.onnx` model weights (`sa.onnx`, `sa_female.onnx`) on initial page load; initialize only on explicit user interaction.
  - Map voice selection cleanly (`female` -> `sa_female` model with `voice: "female"`, `male` -> `sa` model with `voice: "male"`).
  - Fetch `.onnx` weights on demand (with browser `CacheStorage` reuse when warm) and keep both `*.onnx` weights and `frontend/public/js/vendor/` out of Git via `.gitignore`.