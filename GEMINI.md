# Aigaane Project — Gemini Context

Deterministic Sanskrit engine (Pāṇini-faithful). No LLM in new paths.
Live: https://aigaane.in (static) · https://aigaane.in/quanta/ (5-tab React) · https://api.aigaane.in

## Current verified state (Q4-C closed)
- /health: ok · /api/v3/pipeline: 5/5 stages OK · PipelineTab live in /quanta/
- /api/v1/pipeline (LEGACY): returns studio_i_analysis — DO NOT BREAK (smoke test asserts it)
- Tinanta: 9 roots, 351 verified cells (189 ātmanepada across kṛ, labh, dā, cur, vah, jñā; dā loṭ explicitly unverified → 400)
- Sandhi: 5/5 golden cases PASS · Pipeline: 5/5 stages OK
- Tests: 191 passing (166 core + 25 Q4-C ātmanepada)

## P2 dist/ cleanup — COMPLETE (commit c9e05a3)
- Removed public/quanta.bak/ (255 files, 11.91 MB)
- Removed public/legacy/ (81 files, 3.74 MB)
- public/: 422 → 86 files (19.5 → 3.85 MB)
- dist/: 425 → 89 files
- Firebase deploy now uploads ~89 files instead of 424 (4.7× faster)

## Next task
Pick one:
A) P2 cleanup: remove stale dist/legacy/, dist/quanta/legacy/, dist/quanta/quanta/ from public/ and dist/
B) Q7 Itihāsa expansion: add Rāmāyaṇa (~20.5K) + Mahābhārata (~82K) to canon.db

## Rules — never break
1. Do NOT touch /api/v1/pipeline (legacy, smoke test asserts studio_i_analysis)
2. Do NOT regex multi-line Python imports. Read as array, splice by index.
3. FastAPI Body() examples = list of dicts.
4. Run `python -c "import ..."` before push.
5. Use curl.exe or Python urllib for IAST verification (PS mangles UTF-8).
6. pytest binary not on PATH — use `python -m pytest`.
7. When editing HTML/JS anchors, quote style matters (double vs single).