# Aigaane Project — Gemini Context

Deterministic Sanskrit engine (Panini-faithful). No LLM in new paths.
Live: https://aigaane.in (Firebase) · https://api.aigaane.in (Cloud Run asia-south1).

## Current verified state (commit e5bf1db / aigaane-api-00070-pzm)
- /health: ok
- /api/v3/pipeline: 5/5 stages OK
- /api/v1/pipeline (LEGACY): returns studio_i_analysis — DO NOT BREAK
- Golden sandhi: 5/5 PASS · Verb conjugation: 9/9 PASS · Tests: 166

## Next task: PipelineTab.jsx
Create frontend/src/PipelineTab.jsx (5-stage renderer, POST /api/v3/pipeline).
Modify frontend/src/App.jsx to add the pipeline tab.
Reference: NyayaTab.jsx, LexiconTab.jsx.
