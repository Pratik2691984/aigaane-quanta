# Aigaane-Quanta — P0 Vedic Vocal Gap Audit v1.0 (LOCKED)

## 0. Evidence Classification & Governing Rule
- **Verified:** Directly confirmed by read-only inspection of `C:\aigaane-quanta` (Git identity, AST symbol exports, top-level import lines, SQLite `mode=ro` queries, and `pytest -rs`).
- **Partially Verified:** Implementation exists and passes tests, but requires refactoring to satisfy strict Mode 1 / Mode 2 / Mode 3 discipline separation.
- **Proposed / Unverified:** Architectural capability or dataset provenance not yet present on disk.
- **Governing Acceptance Rule:** Aigaane must never certify an audio output as academically correct merely because its symbolic pipeline passed, its waveform is deterministic, or its musical contour is internally consistent. Those are separate evidence claims requiring separate gates.

---

## 1. Repository Identity & Test Baseline (Verified)
- **Repository Root:** `C:/aigaane-quanta`
- **HEAD Commit:** `bbce0ace1c457ad2c34d62fabb1cc1cb5e3009d4` (`bbce0ac`)
- **Branch:** `master` (synced with `origin/master`, `origin/HEAD`)
- **Audit Tree State:** Clean (`frontend/public/mantra.html` WIP stashed as `pre-p0-audit-wip` during DB/AST inspection)
- **Environment:** Python `3.14.4`, Git `2.56.1.windows.1`, PowerShell `5.1.19041.6456`
- **Test Suite (`pytest backend/tests/ -q -rs -p no:cacheprovider`):** **283 passed, 15 skipped** in `22.83s`
  - **7 Skips (Benign 503 Fallback Routes):** `test_chandas_routes.py` (lines 179, 187), `test_lexicon_routes.py` (138, 145), `test_morphology_routes.py` (147, 154), `test_sandhi_routes.py` (123) — skipped because core modules loaded.
  - **8 Skips (Tracked Classical Sandhi Gaps):** `test_sandhi_roundtrip.py` — 7 `no_rule_matches` (`nadīśaḥ`, `vadhūdayaḥ`, `narottamaḥ`, `bhānvudayaḥ`, `saditi`, `taditi`, `tadapi`) and 1 partial restoration (`maharṣiḥ` → `[['maha', 'ṛṣiḥ']]` instead of `['mahā', 'ṛṣiḥ']`).

---

## 2. Verified Import Graph & Transitive Coupling Finding (P0-1)
Direct source inspection of `_svara.py` (335 lines), `_render.py` (109 lines), and `_rhythm.py` (141 lines) established:
- `backend/engine/_svara.py` imports `_sruti` at top level (lines 16–18) and resolves 22-*śruti* Just Intonation ratios inside `generate_vedic_contour()`.
- `backend/engine/_rhythm.py` imports `_tala` at top level (lines 12–15).
- `backend/engine/_render.py` imports `RhythmEvent` from `backend.engine._rhythm` at top level (lines 17–20), which **transitively imports `_tala`** into `sys.modules` even on the `tala_name=None` (`no-tala`) render branch.
- **Architectural Resolution (Option A):** Introduce a dedicated Mode 1 oral recitation module (`backend/engine/vedic/_mode1.py`) and split `derive_svara_labels()` out of `_svara.py` so Mode 1 has **zero direct or transitive import edges** to `_sruti.py`, `_rhythm.py`, or `_tala.py` (verified via subprocess `sys.modules` inspection and runtime monkeypatch guards).

---

## 3. Capability Classification Matrix

| Component / Module | Verified Implementation | Classification | Required Action |
| :--- | :--- | :--- | :--- |
| `backend/engine/_svara.py` | Extracts marks, segments *akṣaras*, derives *jātya*/*pracaya*, imports `_sruti` at top level. | **Partially Verified** | Extract pure label derivation (`derive_svara_labels`); attach accent to vowel nucleus; expand `U+1CD0–U+1CFF` registry and separate `U+0969` from tone marks. |
| `backend/engine/_render.py` | PCM-16 WAV renderer with *kampa* LFO; imports `_rhythm.RhythmEvent` at top level. | **Partially Verified** | Keep for Mode 2/3; introduce `render_wav_oral()` in Mode 1 accepting decoupled time-indexed `(t_ms, hz, voiced)` contours without `_rhythm`. |
| `backend/engine/_rhythm.py` | Maps `ContourEvent` to *tāla* grid (`align_to_tala`), propagates `rest_after_sec`; imports `_tala`. | **Partially Verified** | Restrict `_rhythm.py` and `_tala.py` exclusively to Mode 3 (Musical Sanskrit Rendering). |
| `backend/engine/_chhandas.py` | Computes binary *laghu*/*guru* weights on IAST. | **Partially Verified** | Maintain strict separation between `metrical_weight` (`L`/`G`/`Pluta`) and `phonetic_duration_ms`. |
| `backend/engine/_script.py` | Bidirectional Devanāgarī ⇄ IAST ⇄ SLP1. | **Partially Verified** | Add lossless accent-preserving extended representation (`_vedic_unicode.py` / `_transliteration_extended.py`). |
| `backend/critic/gatekeeper.py` | Fail-closed `KernelEnvelope` validator. | **Partially Verified** | Add explicit abstraction, counterexample validation, and refinement loop (`abstraction.py`, `counterexample.py`, `refinement.py`). |
| `backend/data/canon.db` | 52.64 MB (`frontend/public/sqlite/canon.db` mirror verified at 52.64 MB), 35,504 verses (`10,465` `svara_text` populated). | **Partially Verified** | `verses` table lacks columns for `audio_ref`, `textgrid_ref`, `alignment_status`, `edition`, `license`, and `verified_by`. Add `vedic_metadata` provenance table. |
| `backend/engine/_patha_grammar.py` | Not present on disk. | **Absent / Proposed** | Implement *Śākhā*-verified *Saṃhitā* $\to$ *Pada* $\to$ *Krama* $\to$ *Jaṭā* $\to$ *Ghana* after fixing the 8 skipped classical sandhi round-trip cases. |
| `backend/audio/vedic/` & `tts/` | Not present on disk. | **Absent / Proposed** | Build L6 articulatory phoneme/allophone inventory before any neural vocoder integration. |
| `backend/data/vedic/` | Not present on disk. | **Absent / Proposed** | Ingest first expert-verified `TextGrid` + licence-cleared *Ṛgveda Śākala* audio reference. |

---

## 4. Verified Corpus Evidence (`canon.db` & `frontend/public/sqlite/canon.db`)
- **Database Size:** `52.64 MB` at both `backend/data/canon.db` and `frontend/public/sqlite/canon.db`.
- **`verses` Schema (`35,504` rows):** `['record_id', 'book', 'chapter', 'verse', 'text', 'iast', 'meter', 'source', 'envelope_path', 'recension', 'svara_text', 'text_clean']` (no columns exist yet for audio, alignment, edition, or license provenance).
- **Exact `svara_text` & `recension` Breakdown (Verified):**
  - `rigveda_corpus` (`recension='rgveda_sakala'`): `10,462` total, `10,462` `svara_populated`, `10,462` differentiated (`text != text_clean`).
  - `rigveda_svara_sample` (`rgveda_sakala`, `taittiriya`, `kanva` — 1 each): `3` total, `3` `svara_populated`, `0` differentiated (`text == text_clean`).
  - `Valmiki_Ramayan_Dataset` (`recension=None`): `23,291` total, `0` `svara_populated`.
  - `gita` (`recension=None`): `701` total, `0` `svara_populated`.
  - `gretil.org/upanishads/*` (11 texts, `recension=None`): `1,047` total, `0` `svara_populated`.
  - **Total `svara_text` populated:** `10,465` rows.

---

## 5. Prioritized Implementation Gates (P0 → P2)

| Priority | Gate | Falsifiable Acceptance Criterion |
| :--- | :--- | :--- |
| **P0-1** | **Mode 1 Transitive Isolation (`backend/engine/vedic/_mode1.py` + `test_mode1_isolation.py`)** | Subprocess import check confirms `_tala`, `_sruti`, and `_rhythm` are absent from `sys.modules`; runtime monkeypatch raises `AssertionError` if touched; existing 283 tests remain green. |
| **P0-2** | **Vedic Unicode & Vowel-Nucleus Registry (`_vedic_unicode.py`)** | Full `U+1CD0–U+1CFF` assigned character table; `U+0969` separated from tone marks; accent attached to vowel nucleus. |
| **P0-3** | **Decoupled `VedicPhoneticEvent` Contract (`v3.1`)** | Separate `metrical_weight` (`L`/`G`/`Pluta`) vs. `phonetic_duration_ms`; time-indexed `(t_ms, hz, voiced)` F0 contours; `musical_sruti_overlay = null` in Mode 1. |
| **P0-4** | **Corpus Provenance Table (`vedic_metadata` in `canon.db`)** | SQLite migration adding `edition`, `shakha`, `accent_convention`, `audio_ref`, `alignment_status`, `textgrid_ref`, `license`, and `verified_by`. |
| **P1-1** | **Sandhi Round-Trip Fixes & `_patha_grammar.py`** | Resolve the 8 skipped `test_sandhi_roundtrip.py` cases, then implement *Saṃhitā* $\to$ *Pada* $\to$ *Krama* $\to$ *Jaṭā* $\to$ *Ghana* with golden fixtures. |
| **P1-2** | **L6 Articulatory Phonology (`backend/audio/vedic/`)** | Implement `_phoneme_inventory.py` and `_allophones.py` (*sthāna*, *prayatna*, *ghoṣa*, *prāṇa*, contextual *visarga*/*anusvāra*). |
| **P2-1** | **First Expert-Verified `TextGrid` & Isolated Neural TTS** | Align 1 licence-cleared *Ṛgveda Śākala* verse (`RV 1.1.1`) in Praat `TextGrid`, establish `F0 RMSE` baseline, and keep neural TTS outside Cloud Run image. |
