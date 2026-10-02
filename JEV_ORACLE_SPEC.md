# JEV Oracle — Specification

## Purpose

JEV Oracle is a submission validator that takes any text and reports whether it aligns with the cellular-first design canon.

It uses the **Joint Embedding Validator (JEV)** API as the substrate semantic-meaning referee. JEV is queried with a 14-probe battery covering voice, doctrine, distortions, and numerical content.

## Architecture

```
┌─────────────────────┐
│   submission text   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   14-probe battery  │ (5 voice, 5 doctrine, 5 misquote, ...)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   JEV /v1/systemone │ (POST batch of 14 questions)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  score aggregation  │ (voice, doctrine, misquote, substance, alignment)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      verdict        │ (ACCEPT / REVIEW / DISCUSS / REJECT)
└─────────────────────┘
```

## Probe Battery (14)

| # | Probe | Type | What it tests |
|---|---|---|---|
| 1 | voice_Fleet_Radio | noul | Text in Fleet Radio voice |
| 2 | voice_technical_poetic | noul | Naval-toned, technical-poetic style |
| 3 | doctrine_scar | noul | Cells-are-scars-not-parameters claim |
| 4 | doctrine_witness | noul | Witness-log-is-prediction claim |
| 5 | doctrine_grown | noul | Substrate-grown-not-designed claim |
| 6 | doctrine_oracle | noul | Oracle-heard-not-stored claim |
| 7 | doctrine_lenia | noul | Lenia-flows-where-Conway-stands claim |
| 8 | misquote_scar_params | noul | Catch "cells are parameters" inversion |
| 9 | misquote_witness_past | noul | Catch "witness log is past only" inversion |
| 10 | misquote_designed | noul | Catch "substrate is designed" inversion |
| 11 | misquote_15ports | noul | Catch "15 ports" typo |
| 12 | misquote_oracle_stored | noul | Catch "oracle is stored" inversion |
| 13 | substance_numerical | noul | Contains numerical substrate facts |
| 14 | substrate_alignment | noul | Overall substrate alignment |

## State Format

```python
state = {
    'fleet_radio_seed': 'xochitl',
    'canonical_substrate': {
        'doctrines': [
            'Cells are scars, not parameters.',
            'The witness log is the prediction.',
            ...
        ],
        'voice': 'Fleet Radio — technical-poetic naval transmission',
        'facts': { ... }
    },
    'submission': '<the text being validated>'
}
```

## Output Format

```python
{
    'verdict': 'ACCEPT' | 'REVIEW' | 'DISCUSS' | 'REJECT',
    'voice_score': 0.0-1.0,
    'doctrine_score': 0.0-1.0,
    'misquote_score': 0.0-1.0,  # lower is better
    'substance_score': 0.0-1.0,
    'alignment_score': 0.0-1.0,
    'details': {
        'probe_name': {'value': 0.0-1.0, 'confidence': 0.0-1.0},
        ...
    },
    'meta': {'latency_ms': int, 'input_tokens': int, 'output_tokens': int}
}
```

## Verdict Heuristics

```
if alignment >= 0.85 AND doctrine >= 0.80 AND misquote <= 0.20:
    ACCEPT — strong canonical alignment
elif alignment >= 0.65 AND doctrine >= 0.50 AND misquote <= 0.40:
    REVIEW — partial alignment, scrutinize
elif alignment >= 0.40:
    DISCUSS — weak alignment, may need revision
else:
    REJECT — does not align with canon
```

## Cost & Latency

- Single batch of 14 questions: ~300ms latency, ~1500-3000 input tokens
- Output tokens: ~250-300
- Per submission: ~0.001-0.005 USD at JEV pricing

## Test Results (validated)

| Submission | Voice | Doctrine | Misquote | Alignment | Verdict |
|---|---|---|---|---|---|
| Canonical text | 0.89 | 0.77 | 0.02 | 0.85 | REVIEW (good voice, no oracle claim) |
| Canonical + oracle claim | expected ~0.94 | ~0.94 | 0.02 | ~0.94 | ACCEPT |
| Inverted canonical (cells=params) | 0.32 | 0.02 | 0.98 | 0.02 | REJECT |
| Chatbot-style | 0.12 | 0.04 | 0.27 | 0.14 | REJECT |

## Use Cases

1. **Submission gatekeeping** for cellular-first-design canon: validate incoming prose pieces before admission.
2. **Canon proofreading**: detect accidental inversions ("designed" vs "grown") in existing pieces.
3. **LLM comparison baseline**: every JEV-validated text is canonical; LLM-proposed text can be checked against it.
4. **Writers' room QA**: after each writers' room round, run all outputs through JEV oracle before curation.

## Implementation

`/workspace/repos/jev-quilt/jev_oracle.py`

## Future Enhancements

1. Score-based verdict boundaries (use JEV's score questions for finer granularity)
2. Multi-document comparison (compare submission against specific canonical pieces via cosine)
3. Doctrinal-violation reasoning (have JEV explain WHY it rejected)
4. Active learning: when JEV is uncertain, route to a human reviewer
