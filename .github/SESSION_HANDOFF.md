# Aigaane — Session Handoff

**Last commit:** 1640aa0 (Q3 Session 2 complete: Tala Rhythm Player live)
**Live revision:** (gcloud run services describe aigaane-api --region=asia-south1 --format="value(status.latestReadyRevisionName)")
**Frontend:** https://aigaane.in (static, 7 panels) · https://aigaane.in/quanta/ (5-tab React)
**Backend:** https://api.aigaane.in (15+ endpoints)

## Status: Q4-C v2 + Q7 v2 COMPLETE (full Ramayana + 360 verified verb cells)

### What shipped this session
- Sandhi combiner calls /api/v3/sandhi/combine (DAG fixed, 5/5 golden cases PASS)
- Q4-B: laṅ/lṛṭ/loṭ parasmaipada for kṛ, bhū, gam, as
- Q6-D: semantic lexicon panel (root + quanta)
- Q8: 5-stage deterministic pipeline at /api/v3/pipeline
- /quanta/ routing fix: React app serves at /quanta/ (was serving marketing page)
- Q4-C v2 (cbbdd16): all 198 ātmanepada cells verified across kṛ, labh, dā, cur, vah, jñā (ATMANEPADA_UNVERIFIED empty)

### Verified live endpoints
- /health → ok
- /api/v3/sandhi/combine → candidates[{surface,rule,sutra,score}]
- /api/v3/pipeline → {normalized,tokens,chandas,sruti_map,stages} (5/5)
- /api/v3/morphology/tinanta → 9 roots, 360 cells
- /api/v1/lexicon/semantic → 54 entries
- /api/v1/pipeline (LEGACY) → studio_i_analysis — DO NOT TOUCH

### Data
- _DHATUPATHA: 15 roots
- _tinanta_data.PARADIGMS: 360 cells (144 parasmaipada + 216 ātmanepada)
- _semantic_index: 54 entries · canon.db: 25,039 verses (Gita + 11 Upanishads + full Valmiki Ramayana, all 7 kandas) · _chhandas: 25 meters

### Tests
- 166 core + 31 Q4-C ātmanepada = 197 passing
- 10/10 Q4-B curl · 5/5 golden sandhi · 5/5 pipeline stages

### P2 dist/ cleanup COMPLETE (c9e05a3)
- Removed 336 stale files (15.65 MB)
- Deploy now 4.7× faster (~89 files vs 424)
- Live verified: CSS, sandhi-golden.js, tinanta.js all load correctly

## Zero LLM GUARANTEE COMPLETE (64d94f0)
- Legacy /api/v1/pipeline rewritten to use _pipeline.run_pipeline
- No production endpoint calls EngineAdapter
- Legacy shape preserved: studio_i_analysis still present (smoke test contract)
- parse_envelope now = full deterministic pipeline output (5 stages)
- sruti_table now = real śruti mapping (not static)
- meter_scansion.meter now = detected meter (not hardcoded)

## Q4-C v2 COMPLETE (cbbdd16)
- dā loṭ ātmanepada verified against Kale §389 (9 cells: dattām, dadātām, dadatām, datsva, dadāthām, daddhvam, dadai, dadāvahai, dadāmahai)
- ATMANEPADA_UNVERIFIED set is now empty
- All ātmanepada cells verified for all 6 roots
- Note: earlier local script assertion (set() == set()) was a transient script-ordering issue, not a data problem — runtime state is correct

## Q3 Session 1 COMPLETE (commit bfa952c)
- 22-sruti AudioWorklet player in Studio III tab (/quanta/)
- Play Full Scale + per-row playback + Stop, browser-verified audible

## Next task options
A) P2 cleanup: remove stale dist/legacy/, dist/quanta/legacy/, dist/quanta/quanta/ (30 min)
B) Q7 Itihāsa expansion: Rāmāyaṇa + Mahābhārata into canon.db (2-3 weeks)
C) P3 Q4-C v2: verify dā loṭ ātmanepada against primary source

### Gotchas (do not repeat)
1. **PowerShell UTF-8**: Invoke-RestMethod mangles UTF-8 (ā→Ä). Use curl.exe or Python urllib.
2. **Regex on multi-line imports**: read as array, splice by index. Never regex import blocks.
3. **Body() examples**: examples=[{...}] list of dicts.
4. **Deploy fails on SyntaxError**: run `python -c "import ..."` before push.
5. **pytest binary not on PATH**: use `python -m pytest`.
6. **Anchor strings in replace**: quote style (single vs double) matters.
7. **Firebase rewrites**: /quanta/** → /quanta.html, must come BEFORE catch-all **

### Resume prompt for new chat
> Continuing Aigaane at C:\aigaane-quanta. Read .github/SESSION_HANDOFF.md. Q4-C v1 complete (189 ātmanepada cells, dā loṭ unverified). Both frontends live. Next: pick from the roadmap — P2 cleanup or Q7 Itihāsa expansion.

## Q3 Session 2 COMPLETE (Tala Rhythm Player)
- 46 Carnatic talas in Studio III dropdown
- BPM control (30-240)
- Play/Stop with cycle pulse + sam accent (360Hz on akshara 1, 240Hz elsewhere)
- Visual akshara highlight tracks current beat
- Same AudioWorklet as 22-sruti player

## LLM Retirement COMPLETE (a05968e)

Two commits, both deployed, both verified via CI + smoke.

- `09c64bb` — `_neural_fallback.py` no longer imports or calls `genai`; `is_llm_available()` returns False; Gemini branch removed.
- `a05968e` — `google-genai` removed from `requirements.txt`.

### What "Retire Parse" actually was

The prior handoff described this as a 1-2 session build of a deterministic compound parser. That was a misdiagnosis. The real picture:

- Chain: `legacy_parse` -> `EngineAdapter.parse` -> `legacy_engine.parse` -> `_neural_fallback.fallback_parse` (terminal fallback only)
- `legacy_engine.py` (32 KB) was already deterministic pure Python
- The LLM was a single terminal branch, not the whole parse path
- Scope was THREE routes, not one: `/api/v1/parse`, `/api/v1/samasa/split`, `/api/v3/samasa/split` (all three mounted via `EngineAdapter`)
- Production `GEMINI_API_KEY` was never set — the LLM branch had been dead in prod all along
- Local testing showed the branch fired but only ever produced `heuristic-degraded-fallback` output (Gemini threw or returned unparseable JSON)
- Net user-visible change: zero. Baseline diff before/after was byte-identical across all 5 test inputs.

### Verified state after retirement

- HEAD: a05968e
- 197 passed, 15 skipped, 1.72s runtime (was 5.25s — genai import cost gone)
- CI #139 / Deploy Backend #67 / Smoke #37 all green
- `import google` in backend source (excl. venv): zero hits
- Docker image no longer installs `google-genai`

### Follow-ups (not this session)

- `AigaaneInspector.jsx:20` fetches `/api/v1/aigaane/parse`. That route does NOT exist — grep confirms zero decorators. Inspector UI is broken in production. Fix: repoint to `/api/v1/parse`, or add the route.
- `/health` still returns `"architecture":"Neuro-Symbolic"` — stale string; one-line change.
- `requirements.txt` still has `# Trigger deploy` / `# Force redeploy` debris lines at the bottom.
- `_neural_fallback.py` has unused `os`, `json` imports.

### Note on prior handoff accuracy

The handoff called `/api/v1/parse` the "last LLM path" and estimated 1-2 sessions. Correct on intent, wrong on mechanism and scope. The actual work was 2 small commits (~25 min). Future handoffs should verify mechanism (which file, which call site) and scope (how many routes) before estimating effort.
