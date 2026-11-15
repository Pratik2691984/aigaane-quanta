# Aigaane Project — Gemini Context

Deterministic Sanskrit engine (Pāṇini-faithful). No LLM in new paths.
Live: https://aigaane.in (static) · https://aigaane.in/quanta/ (5-tab React) · https://api.aigaane.in

## Current verified state (Q4-C closed)
- /health: ok · /api/v3/pipeline: 5/5 stages OK · PipelineTab live in /quanta/
- /api/v1/pipeline (LEGACY): returns studio_i_analysis — DO NOT BREAK (smoke test asserts it)
- Tinanta: 9 roots, 360 verified cells (198 ātmanepada across kṛ, labh, dā, cur, vah, jñā; ATMANEPADA_UNVERIFIED empty at commit cbbdd16)
- Sandhi: 5/5 golden cases PASS · Pipeline: 5/5 stages OK
- Tests: 197 passing (166 core + 31 Q4-C ātmanepada)

## P2 dist/ cleanup — COMPLETE (commit c9e05a3)
- Removed public/quanta.bak/ (255 files, 11.91 MB)
- Removed public/legacy/ (81 files, 3.74 MB)
- public/: 422 → 86 files (19.5 → 3.85 MB)
- dist/: 425 → 89 files
- Firebase deploy now uploads ~89 files instead of 424 (4.7× faster)

## Zero LLM GUARANTEE — COMPLETE (commit 64d94f0)
- /api/v1/pipeline retired: now backed by deterministic _pipeline.run_pipeline
- No production endpoint calls EngineAdapter anymore
- All responses include deprecated:True + replacement:/api/v3/pipeline
- parse_envelope now contains full 5-stage deterministic output

## Q4-C v2 COMPLETE (cbbdd16)
- dā loṭ ātmanepada verified against Kale §389 (juhotyādi + khari ca 8.4.55)
- 9 cells: dattām, dadātām, dadatām, datsva, dadāthām, daddhvam, dadai, dadāvahai, dadāmahai
- ATMANEPADA_UNVERIFIED is now empty
- All 6 roots fully verified: kṛ, labh, dā, cur, vah, jñā
- Total verified verb cells: 207 ātmanepada (was 189 + 9 dā loṭ + 9 reindexed)

## Q7 v2 COMPLETE (commit e876bfb)
- Ingested full Valmiki Ramayana (23,291 verses, all 7 kandas) into canon.db + frontend SQLite
- Total canon.db verses: 25,039 (FTS5 rebuilt; dharma* matches rose from 6 to 807, rama* to 2,118)

## Q3 Session 1 COMPLETE (commit bfa952c)
- 22-sruti AudioWorklet player in Studio III tab (/quanta/)
- Play Full Scale + per-row playback + Stop, browser-verified audible

## Next task
Pick one:
A) P2 cleanup: remove stale dist/legacy/, dist/quanta/legacy/, dist/quanta/quanta/ from public/ and dist/
B) Q7 Mahābhārata expansion: add Mahābhārata (~82K verses) to canon.db (Ramayana already complete)

## Rules — never break
1. Do NOT touch /api/v1/pipeline (legacy, smoke test asserts studio_i_analysis)
2. Do NOT regex multi-line Python imports. Read as array, splice by index.
3. FastAPI Body() examples = list of dicts.
4. Run `python -c "import ..."` before push.
5. Use curl.exe or Python urllib for IAST verification (PS mangles UTF-8).
6. pytest binary not on PATH — use `python -m pytest`.
7. When editing HTML/JS anchors, quote style matters (double vs single).

## Q3 Session 2 COMPLETE (Tala Rhythm Player)
- 46 Carnatic talas in Studio III dropdown
- BPM control + Play/Stop + visual akshara highlight

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
