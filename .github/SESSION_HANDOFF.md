# Aigaane — Session Handoff

**Last commit:** `e5bf1db` (master)
**Live revision:** `aigaane-api-00070-pzm` (Cloud Run, 100% traffic)
**Frontend:** https://aigaane.in · **Backend:** https://api.aigaane.in

## Current state

### Verified live endpoints
- `/health` → status=ok, version=2.3.0-legacy-ui-bridge
- `/api/v3/sandhi/combine` → candidates[{surface,rule,sutra,score}]
- `/api/v1/lexicon/semantic?stem=X` → {dhatu,gana,gana_number,nirukta,gloss,synonyms,antonyms,related,citations}
- `/api/v3/morphology/tinanta` → {surface,source:'table'|'generated',confidence}
- `/api/v3/morphology/tinanta/paradigm` → {rows[{purusha,cells[{vacana,surface,source}]}]}
- `/api/v3/morphology/tinanta/dhatus` → {dhatus[...]}
- `/api/v3/pipeline` → {input,normalized,tokens,chandas,sruti_map,stages,warnings}
- `/api/v1/pipeline` (LEGACY, smoke test target) → {studio_i_analysis,...} — DO NOT TOUCH

### Frontend panels live
- aigaane.in/: Sandhi Combiner, golden 5-case card, verb conjugation, Kosha+semantic, Chandas, Subanta, audio, Itihasa — all present
- aigaane.in/quanta/: 4 tabs (Inspector, Nyaya, Lexicon, Studio3) — no pipeline tab yet

### Data
- _DHATUPATHA: 15 roots, all 10 gaṇas
- _tinanta_data.PARADIGMS: 4 roots (kṛ, bhū, gam, as) × 4 lakāras × 9 cells
- _semantic_index: 54 entries · canon.db: 1,748 verses · _chhandas: 25 meters

### Tests
- 166 passing · 10/10 Q4-B curl · 5/5 golden sandhi card live

## Next task: Pipeline frontend tab

Create `frontend/src/PipelineTab.jsx`:
- Verse textarea, sample inputs, Analyze button
- POST `{API_URL}/api/v3/pipeline` with `{text}`
- Render 5 collapsible cards: Normalize, Tokens, Chandas, 22-Sruti Map, Stages
- Style: bg #0f172a, cards #1e293b, accents #a78bfa and #38bdf8, text #e2e8f0

Modify `frontend/src/App.jsx`:
- Import PipelineTab
- Add `{ id: 'pipeline', label: 'Pipeline' }` to tabs array
- Add `{activeTab === 'pipeline' && <PipelineTab />}`

Reference: frontend/src/NyayaTab.jsx, frontend/src/LexiconTab.jsx

Build: `cd frontend; npm run build`, then git add + commit + push. Deploy ~35s.

## Roadmap after pipeline tab
- P1: Q4-C Ātmanepada completion (1 session)
- P2: Q7 Itihāsa expansion (2-3 weeks)
- P2: Audio worklet + tāla dropdown (1-2 sessions)
- P2: dist/ cleanup (30 min)
- P3: Retire legacy /api/v1/pipeline (uses LLM)
- P3: Layer-A derivation engine (~15 sessions)

## Gotchas (do not repeat)

1. **PowerShell UTF-8**: `Invoke-RestMethod` mangles UTF-8 (ā→Ä, ṣ→á¹£). Use `curl.exe` or Python urllib for verification.
2. **Regex on multi-line imports**: two main.py corruptions. Rule: read as array, splice by index, write back. Never regex import blocks.
3. **Body() examples**: must be `examples=[{...}]` (list of dicts), not `examples=['key': val]`.
4. **Firebase cache**: explicit headers in firebase.json (HTML no-cache, JS/CSS max-age=300). New file types need headers.
5. **Vite copyPublicDir**: public/ auto-copied to dist/ on build. Just edit + build.
6. **Deploy fails on SyntaxError**: Cloud Run health check catches it, traffic stays on last healthy rev. Always `python -c 'import ...'` before push.
6. **Sandhi DAG vs result box**: separate code paths. If they disagree, cache or wrong endpoint.

## Environment
- Local: C:\aigaane-quanta (Win PowerShell 5.1)
- Repo: Pratik2691984/aigaane-quanta
- Firebase project: aigaane-engine-2026
- Cloud Run: aigaane-api, asia-south1
- Auto-deploy on push to master (CI + Frontend/Backend + Smoke Test)

## Verification commands (curl-safe)
```powershell
curl.exe -s https://api.aigaane.in/health
curl.exe -s -X POST https://api.aigaane.in/api/v3/pipeline -H 'Content-Type: application/json' -d '{"text":"dharmakṣetre kurukṣetre"}'
curl.exe -s 'https://api.aigaane.in/api/v3/morphology/tinanta?dhatu=bh%C5%AB&lakara=la%E1%B9%85'
curl.exe -s 'https://api.aigaane.in/api/v1/lexicon/semantic?stem=dharma'
```

## Paste into new DeepSeek chat

> Continuing Aigaane at C:\aigaane-quanta, commit e5bf1db, live revision aigaane-api-00070-pzm. All backend endpoints verified. Read .github/SESSION_HANDOFF.md for full state. Next: create frontend/src/PipelineTab.jsx and wire into App.jsx. Start by having me run `Get-Content .github\SESSION_HANDOFF.md`, then walk me through PipelineTab.jsx + App.jsx changes.