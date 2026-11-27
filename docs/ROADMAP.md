# Aigaane-Quanta Master Roadmap

## ✅ Completed & Locked
*   **Pillar 1: Kernel & Adapter:** Deterministic grammar.
*   **Pillar 2: CEGAR Gatekeeper:** Two-tier attestation (Lexicon + FTS5 fallback).
*   **Pillar 3: Studio III Acoustics:** Tāla engine, 22-śruti JI, MIDI export.
*   **API Surface:** 55 dual-mounted endpoints.
*   **Category F (Nyāya Verifier):** 5-step syllogistic logic (Commit `1cc0587`, Tag `v2.0.4-nyaya`).

## ⏳ Pending
*   **Category A (Production Kosha):** Wiring the 1.5M FTS5 DB into the production Docker container (deferred; local dev uses `_lexicon.py`).
*   **Category C (Golden Corpus):** Expand from 81 to 100+ verified cases.
*   **Category D (Quanta Frontend):** React UI port.
*   **Category G (Deployment):** Cloud Run containerization.
*   **Category H (Docs):** This document is now current.
### Advanced Lab & Synthetic Evidence Ledger (`/advanced-lab/`)

* **Status:** `EXPERIMENTAL` / `UNVERIFIED` — strictly sandboxed under `/advanced-lab.html` and `/advanced-lab/*` (including `/advanced-lab/ai-studio-3126.html` and `/advanced-lab/tfqn-v4.html`).
* **Scope & Isolation:**
  * Houses experimental quantum, reversible arithmetic, AI sandbox, and Bindu Point visualization/execution prototypes without altering deterministic Sanskrit grammar/prosody, Canon provenance, Mode 1 Vedic recitation, or 22-*śruti* / *tāla* / MIDI synthesis.
  * Keeps `canon.db` outside Git commits and holds Firebase Hosting / Cloud Run deployments until explicitly approved.
* **Synthetic Evidence Format (`schema_version: "1.0.0"`):**
  * Captures `run_id`, `timestamp_utc`, module/route and active track (`AI Research` / `Quantum`), execution parameters (node, frequency, laminar viscosity, Tripundra qutrit state, `thinking_level`, and input payload digest), and `simulation_mode: "synthetic"`.
  * Explicitly sets `verification.status` to `"unverified_experimental"`, `measured_hardware` to `false`, and `authoritative_for_core_domain` to `false` until independently verified.
