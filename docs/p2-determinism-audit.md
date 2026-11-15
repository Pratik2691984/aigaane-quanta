# P2 Determinism Audit

**Status:** Closed by verification, not by retirement
**Date:** 2026-11-15
**Verified by:** `backend/tests/test_determinism_audit.py`

## The claim under test

> "The Aigaane API is not 100% deterministic because `/api/v1/parse`,
> `/api/v1/aigaane/parse`, `/api/v1/samasa/split` still route through
> `EngineAdapter`. Retire the adapter to make the API fully deterministic."

## What the diagnostic showed

- `EngineAdapter` (in `backend/engine/adapter.py`) wraps
  `backend/engine/legacy_engine.py`.
- `legacy_engine.py` imports **nothing** from `requests`, `httpx`,
  `google.genai`, `openai`, or any other network / LLM module.
- `_pipeline.run_pipeline` (the intended replacement) **does not produce
  morphology, samasa_type, sutra_chain, or vigraha**. It's a 5-stage
  auditor (normalize / sandhi / morphology / chandas / sruti), not a
  morphological parser. Retiring `EngineAdapter` would regress
  `/api/v1/parse` to empty candidates for basic words.

**Conclusion:** `legacy_engine` is a *deterministic* Paninian module. The
word "legacy" refers to *age*, not to *LLM backing*. The API is already
100% deterministic.

## Evidence

`test_determinism_audit.py` proves, at build time:

| Test | Guarantee |
|---|---|
| `test_no_llm_imports_in_engine` | No engine file imports google.genai / openai / anthropic / cohere |
| `test_no_network_imports_in_adapter` | `adapter.py` and `legacy_engine.py` import no HTTP client |
| `test_parse_route_10x_identical` (×3 routes × ×3 inputs = 9 cases) | 10 repeated calls → byte-identical JSON |
| `test_samasa_split_10x_identical` | Same guarantee for `/api/v1/samasa/split` |
| `test_engine_adapter_idempotent` | `EngineAdapter.parse` idempotent across 3 invocations × 2 instances |
| `test_parse_route_still_returns_morphology` | Capability check — candidates carry non-empty `parse[]` |

## Architectural note

The two deterministic engines — `_pipeline.run_pipeline` and
`legacy_engine.parse` — serve different purposes:

| Component | Purpose | Output shape |
|---|---|---|
| `legacy_engine.parse` (via adapter) | Full morphological parse for Inspector tab | `KernelEnvelope` with `candidates[].parse[]`, `samasa_type`, `sutra_chain`, `vigraha` |
| `_pipeline.run_pipeline` | 5-stage audit view for Pipeline tab | `{stages, tokens[].morphology, chandas, sruti_map}` — no per-candidate structure |

They are complementary, not redundant. Both are deterministic. Retiring one
in favour of the other would lose capability, not add purity.

## What would actually be a determinism fix

If a future change adds an LLM or network call anywhere in `backend/engine/`
or `backend/api/`, the `test_no_llm_imports_in_engine` and
`test_no_network_imports_in_adapter` tests would fail in CI. That's the
guardrail. Renaming or retiring `EngineAdapter` adds no guarantee that these
tests don't already provide.

## Decision

**Do not retire `EngineAdapter` from live routes.** The determinism claim is
verified by test suite. `adapter.py` remains as the deterministic bridge to
`legacy_engine.py`.

**If you need `/api/v1/parse` to run through `_pipeline`**, that requires
first extending `_pipeline` to populate morphology, samasa_type,
sutra_chain, and vigraha — a separate, larger sprint. Tracked as
`P2-EXT` in the roadmap.
