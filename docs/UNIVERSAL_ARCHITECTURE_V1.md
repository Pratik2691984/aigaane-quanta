# Aigaane-Quanta Universal Architecture Specification v1.0

- **Document Status:** FROZEN SPECIFICATION — BOUNDARIES, CONTRACTS & EVIDENCE QUALIFIERS
- **Target Repository:** `C:\aigaane-quanta` (`master`, P0 baseline `27e4a19987ca21dbc12fffb6e40c41948e391d44`)
- **Governance Rule:** This specification freezes architectural boundaries, authority separation, result classification, governing contracts, and maturity definitions. It does **not** treat passing unit tests, populated metadata rows, byte-identical file hashes, or dual router mounts as proof of linguistic completeness, recension authority, expert verification, or production readiness.

---

## 1. Evidence-Qualified Baseline (P0 / P0.1 / P0.2)

| Area | Verified Evidence Summary | Permitted Status |
| :--- | :--- | :--- |
| P0 test baseline | `pytest backend/tests/ -q` reported `472 passed, 7 skipped` (`19.58s` with `-rs -p no:cacheprovider`); all 7 skips are explicit 503-fallback guard skips when modules are loaded. | `TESTED` |
| P0.1 corpus metadata | `114,341` `verses` rows; `15,430` `vedic_metadata` rows (`98,911` verses without metadata row); `0` `expert_verified`, `0` populated audio/TextGrid pairs. | `IMPLEMENTED — NOT VERIFIED` |
| P0.2-A Git inventory | `canon.db` copies, `valmiki_ramayana_shlokas.json`, `ninada.bundle.mjs`, and `ort-wasm-simd-threaded.jsep.wasm` are `tracked=False, ignored=True`; `spoken_preview.js` is `tracked=True, ignored=False`. | `TESTED` |
| P0.2-B Pāṇinian core | Rule-tagged sandhi/morphology/pipeline/gatekeeper/Nyāya modules exist; full step-by-step `prakriyā` derivation graphs and complete conflict/asiddhatva adjudication are not yet demonstrated. | `PARTIALLY IMPLEMENTED` |
| P0.2-C database copies | `backend/data/canon.db`, `frontend/public/sqlite/canon.db`, and `frontend/dist/sqlite/canon.db` match in byte size (`147,795,968`) and SHA-256 (`c05495e7f35e81c1e23533e608fd83a2e1f07f11470165194f20c8838062d583`). | `TESTED — BYTE IDENTITY` |
| P0.2-D provenance | `0` null/empty `source` values in `verses` and `0` orphaned `vedic_metadata` rows, but `license` is unverified/unknown across `15,430` rows and `5` `source_registry` rows, and `verified_by` is unpopulated. | `IMPLEMENTED — INCOMPLETE` |
| P0.2-E API versions | 12 routers are mounted under `/api/v1/*` and `/api/v3/*` (with `/api/v1/pipeline/v2` and `/api/v3/pipeline`), plus legacy/health/diagnostic endpoints; full request/response/error parity is unproven. | `MOUNTING VERIFIED` |
| P0.2-F heuristic fallback | `backend/engine/_neural_fallback.py` has `_GENAI_AVAILABLE = False` and `is_llm_available() -> False`, and `legacy_engine.py` calls `fallback_parse()` when deterministic parsing yields no match. | `IMPLEMENTED — REACHABLE` |

### Audit Scope Qualifications
- The P0.2-B/F inspection inspected selected source lines, symbol names, and targeted checks—not complete function bodies or an exhaustive call graph across every route and `_pipeline.run_pipeline()`.
- Passing unit tests (`472 passed, 7 skipped`) do not establish P1, P3, P4, or P5 linguistic or traditional correctness.

---

## 2. Independent Maturity States (No Automatic Promotion)

| State | Meaning |
| :--- | :--- |
| `DESIGNED` | Specification or architectural contract exists. |
| `IMPLEMENTED` | Code or data structure exists in the repository. |
| `TESTED` | Defined automated tests or checks pass under recorded conditions. |
| `EXPERT_VERIFIED` | Qualified human / domain-expert review is documented. |
| `PRODUCTION_VERIFIED` | Deployed behavior and runtime artifacts have been independently checked. |

A component may **never** advance automatically from one state to another. Passing tests, HTTP 200 responses, non-null metadata fields, or matching file hashes do not establish `EXPERT_VERIFIED`.

---

## 3. Architectural Layers (`P0–P8`) & Corrections

| Layer | Responsibility | Required Scope & Qualifications |
| :--- | :--- | :--- |
| `P0` | Governance & evidence | Release gates, provenance ledger, reproducibility, maturity states, and audit controls. |
| `P1` | Sanskrit scripts & *Śikṣā* | Unicode (`U+0951–U+0952`, `U+1CD0–U+1CFF`), `Devanāgarī` / `IAST` / `SLP1` normalization, and articulatory/phonological contracts. Existing components do not yet establish full *Śikṣā* or complete Vedic-extension contract verification. |
| `P2` | Pāṇinian computational core | Rule registry, `adhikāra`, `anuvṛtti`, `prakriyā` intermediate states, rule ordering (`1.4.2 vipratiṣedha`, `6.4.22` & `8.2.1 asiddhatva`, `antaraṅga–bahiraṅga`), and derivation traces. Rule-tagged sandhi/morphology modules are not a complete `prakriyā` interpreter. |
| `P3` | Vedic *Svara* | Vedic accent classification, recension-specific conventions, and structured `svara` events. Existing modules do not prove recension-level or expert correctness. |
| `P4` | *Pāṭha* & *Chandas* | Recitation sequence grammar (*Saṃhitā*, *Pada*, *Krama*, *Jaṭā*, *Ghana*), metrical analysis, and separation of `mātrā` from measured/synthesized acoustic duration (`ms`). Existing modules do not prove recension-level or expert correctness. |
| `P5` | Knowledge authority | Lexicon, mantra, *bīja*, *viniyoga*, and *Nyāya* 5-member inference (*pratijñā*, *hetu*, *udāharaṇa*, *upanaya*, *nigamana*). A non-empty `sūtra_chain` is not a complete five-member *Nyāya* proof. |
| `P6` | Corpus & textual witnesses | Ingestion, `source_registry`, edition, recension, provenance, and verification. Structural presence does not equal verified licensing, alignment, or authority. |
| `P7` | Audio & deterministic synthesis | Phoneme timing, alignment, acoustic models, DSP, and recitation rendering. Zero `expert_verified` alignments or populated audio/TextGrid pairs exist in the audited metadata. |
| `P8` | Neural research & Advanced Lab | Experimental models, comparative evaluation, adapters, and isolated research interfaces (`advanced-lab.html` / `/advanced-lab/`). Must remain isolated and non-authoritative. |

---

## 4. Five Governing Contracts & Mandatory Fallback Invariant

1. **Linguistic Derivation Contract:** Deterministic, reproducible, and rule-governed transformations with explicit provenance rather than silent heuristic or neural substitution.
2. **Vedic Recitation Contract:** *Śākhā*- and recension-aware handling; fail closed on missing *svara* marks or unverified recensions rather than inventing contours or conflating Vedic oral recitation with musical *śruti*/*tāla*.
3. **Musical Rendering Contract:** Isolated from Vedic accent authority, Sanskrit grammatical derivation state, and canonical text mutation.
4. **Corpus Provenance Contract:** Source-, edition-, recension-, license-, alignment-, and reviewer-aware; unverified fields remain explicit (`unknown` / `none` / `null`) and are never promoted by default.
5. **Neural Research Contract:** Non-authoritative; neural or heuristic outputs may propose or assist in isolated contexts, but cannot silently promote generated results into canonical knowledge or mutate authoritative derivations.

### Mandatory Result Classification & Invariant
> **Invariant:** No heuristic or neural output may be represented as a successful deterministic Pāṇinian derivation.

- `DETERMINISTIC_DERIVATION`: Validated rule-governed result with derivation evidence.
- `AMBIGUOUS_DERIVATION`: Multiple candidate derivations requiring adjudication.
- `HEURISTIC_UNVERIFIED`: Guessed or inferred result without a complete derivation (including `fallback_parse()` output); **must never** satisfy a `DETERMINISTIC_DERIVATION` contract even if accepted by a downstream gatekeeper.
- `UNRESOLVED`: No defensible result.

---

## 5. Explicit Non-Goals & Execution Order

### Non-Goals for Specification Freeze
- Do **not** modify `index.html`, `canon.html`, `cabinet.html`, `mantra.html`, `gandharva.html`, existing API routes, or `canon.db` during specification freeze.
- Do **not** commit, push, or deploy to Cloud Run or Firebase Hosting without explicit approval.
- Do **not** advance components to `EXPERT_VERIFIED` or `PRODUCTION_VERIFIED` without matching evidence.

### Execution Order After Freeze
1. **Freeze `docs/UNIVERSAL_ARCHITECTURE_V1.md`** with contracts, layer boundaries, maturity states, evidence qualifiers, and non-goals.
2. **P0.2-F Hardening:** Introduce explicit `HEURISTIC_UNVERIFIED` result classification and regression tests so heuristic outputs cannot be misclassified as deterministic derivations in adapter, API, or gatekeeper flows.
3. **P0.2-E API Contract Audit:** Compare `/api/v1/*` and `/api/v3/*` request/response models, status codes, error behavior, and route tests without removing or renaming endpoints.
4. **P2 Derivation-Engine Design:** Specify rule registry, derivation state, rule ordering/adjudication, and reproducible traces for *gacchati* and *rāmaḥ* prior to implementing the interpreter.