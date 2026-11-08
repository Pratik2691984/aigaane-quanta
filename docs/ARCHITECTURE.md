# Aigaane-Quanta: System Architecture

**Version:** 2.0.4 (Nyāya Verified)
**Baseline Commit:** `v2.0.4-nyaya`

## 1. The Dual-Environment Reality
To ensure sub-second test iteration while maintaining production scale, Aigaane-Quanta operates in two distinct states:

*   **Local Development (Speed-First):** Uses the hardcoded `backend/engine/_lexicon.py` (thousands of high-frequency Pāṇinian stems) for instant lookups. It does *not* require the 1.5M record database to boot or pass tests.
*   **Production (Scale-First):** Cloud Run containers mount the pre-compiled 1.5M headword FTS5 SQLite index (`kosha_1.5m.db`). The API contract (`KernelEnvelope`) is identical in both environments.

## 2. The Three Architectural Pillars

### Pillar 1: Pāṇinian Grammar & Morphology
*   **Location:** `backend/engine/`
*   **Core Files:** `legacy_engine.py`, `_sandhi.py`, `_samasa.py`, `_morphology.py`
*   **Invariant:** Deterministic rule application. Zero neural hallucination in core symbolic parsing.

### Pillar 2: CEGAR Envelope & Nyāya Verification
*   **Location:** `backend/critic/` and `backend/nyaya/`
*   **Core Files:** `gatekeeper.py` (Attestation), `adapter.py` (Envelope reshaper), `nyaya/verifier.py` (5-step syllogism).
*   **Invariant:** Candidates must be lexically attested (Gatekeeper) and logically verified (Nyāya) before being returned to the client.

### Pillar 3: Upaveda Studios & Acoustics
*   **Location:** `backend/audio/`
*   **Core Files:** `_chhandas.py` (Piṅgala binary meter), `_sruti.py` (22-śruti JI), `_tala.py` (Diophantine congruence).
*   **Invariant:** Audio math is mathematically pure and independently testable.

## 3. API Transport (Dual-Mount)
*   **Location:** `backend/api/main.py`
*   **Canonical Routes:** `/api/v3/*` (e.g., `/api/v3/nyaya/verify`, `/api/v3/lexicon/lookup`)
*   **Deprecated Aliases:** `/api/v1/*` (kept for backward compatibility)
*   **Safety:** CORS policies explicitly allow `localhost:5173` and `aigaane.in`.