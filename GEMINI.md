# Aigaane Project — Gemini Context

Deterministic Sanskrit engine (Panini-faithful). No LLM in new paths.
Live: https://aigaane.in (static) · https://aigaane.in/quanta/ (5-tab React) · https://api.aigaane.in (Cloud Run asia-south1).

## Current verified state (commit 3bba2fc / aigaane-api-00070-pzm)
- /health: ok · /api/v3/pipeline: 5/5 stages OK · PipelineTab live in /quanta/
- /api/v1/pipeline (LEGACY): returns studio_i_analysis — DO NOT BREAK (smoke test asserts it)
- Golden sandhi: 5/5 PASS · Verb conjugation: 9/9 PASS · Tests: 166

## Next task: Q4-C (Atmanepada completion)
Expand atmanepada paradigms in backend/engine/_tinanta_data.py (kr, labh, da, cur, vah, jna) and verify via /api/v3/morphology/tinanta/paradigm.
