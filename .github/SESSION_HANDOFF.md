# Aigaane — Session Handoff

**Last commit:** `930afca` (master)
**Live revision:** `aigaane-api-00070-pzm` (Cloud Run, 100% traffic)
**Frontend:** https://aigaane.in (static) · https://aigaane.in/quanta/ (5-tab React app)
**Backend:** https://api.aigaane.in (12 endpoints live)

## Current state (Q8 closed)

### Verified live endpoints
- `/health` -> status=ok, version=2.3.0-legacy-ui-bridge
- `/api/v3/sandhi/combine` -> candidates[{surface,rule,sutra,score}]
- `/api/v1/lexicon/semantic?stem=X` -> {dhatu,gana,gana_number,nirukta,gloss,synonyms,antonyms,related,citations}
- `/api/v3/morphology/tinanta` -> {surface,source:'table'|'generated',confidence}
- `/api/v3/morphology/tinanta/paradigm` -> {rows[{purusha,cells[{vacana,surface,source}]}]}
- `/api/v3/morphology/tinanta/dhatus` -> {dhatus[...]}
- `/api/v3/pipeline` -> {input,normalized,tokens,chandas,sruti_map,stages,warnings} (5/5 stages live)
- `/api/v1/pipeline` (LEGACY, smoke test target) -> {studio_i_analysis,...} — DO NOT TOUCH

### Frontend surfaces (both live)
- `aigaane.in/`: Sandhi Combiner, golden 5-case card, verb conjugation, Kosha+semantic, Chandas, Subanta, audio, Itihasa
- `aigaane.in/quanta/`: 5-tab React app — Aigaane Inspector, Nyaya Verifier, Lexicon (morphology + semantic), Studio III (Tala), Pipeline (5-stage deterministic renderer)

### Data & Tests
- _DHATUPATHA: 15 roots across all 10 ganas · PARADIGMS: 4 roots (kr, bhu, gam, as) x 4 lakaras x 9 cells
- _semantic_index: 54 entries · canon.db: 1,748 verses · _chhandas: 25 meters
- 166 passing pytest tests · 10/10 Q4-B curl · 5/5 golden sandhi · 5/5 pipeline stages live

## Next task: Q4-C (Atmanepada completion)
- Complete atmanepada paradigms for kr, labh, da, cur, vah, jna in backend/engine/_tinanta_data.py
- Verify via /api/v3/morphology/tinanta/paradigm and update tinanta.js label

## Roadmap after Q4-C
- P2: Q7 Itihasa expansion (Ramayana, Mahabharata)
- P2: Audio worklet + tala dropdown in /quanta/
- P2: dist/ cleanup (stale dist/legacy/, dist/quanta/legacy/, dist/quanta/quanta/)
- P3: Retire legacy /api/v1/pipeline (LLM-backed)
- P3: Layer-A derivation engine

## Gotchas (do not repeat)
1. **PowerShell UTF-8**: `Invoke-RestMethod` mangles UTF-8. Use `curl.exe` or Python urllib for verification.
2. **Regex on multi-line imports**: Read main.py as array, splice by index, write back. Never regex import blocks.
3. **Body() examples**: Must be `examples=[{...}]` (list of dicts).
4. **Firebase cache & rewrites**: HTML is no-cache; /quanta/** rewrites to /quanta.html.
5. **Deploy fails on SyntaxError**: Always run `python -c 'import ...'` locally before push.

## Resume prompt
> Continuing Aigaane at C:\aigaane-quanta (commit 3bba2fc, rev aigaane-api-00070-pzm). Q8 is closed and both frontends (aigaane.in/ and 5-tab aigaane.in/quanta/) are live. Read .github/SESSION_HANDOFF.md and start Q4-C (Atmanepada completion in _tinanta_data.py).