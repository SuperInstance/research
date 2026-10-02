# JEV Tutorial — Using the Joint Embedding Validator

## What is JEV?

JEV (Joint Embedding Validator) is a TypeSafe AI API that answers `noul` (yes/no with probability), `choice` (pick from criteria), and `score` (1-5 rubric) questions about a `state` (any content).

**Base URL**: `https://api.typesafe.ai`
**Endpoint**: `POST /v1/systemone`
**Models**: `jev-latest`, `jev-1.13.0`, `jev-preview`
**Auth**: `Authorization: Bearer <TYPESAFEAI_KEY>`

## Wire Protocol

```json
POST /v1/systemone
{
  "model": "jev-latest",
  "state": {"any": "content you want validated"},
  "questions": {
    "q1": {"type": "noul", "instructions": "Is this X?"},
    "q2": {"type": "choice", "instructions": "Pick Y", "criteria": {"a": "desc a", "b": "desc b"}},
    "q3": {"type": "score", "instructions": "Rate Z", "criteria": ["1", "2", "3", "4", "5"]}
  }
}

Response:
{
  "model": "jev-latest",
  "answers": {
    "q1": {"type": "noul", "noul": 0.85, "confidence": 0.92},
    "q2": {"type": "choice", "choice": "a", "confidence": 0.78, "probabilities": {"a": 0.85, "b": 0.15}},
    "q3": {"type": "score", "score": 4.2, "confidence": 0.81, "probabilities": {"0": 0.05, "1": 0.1, "2": 0.15, "3": 0.5, "4": 0.2}}
  },
  "usage": {"input_tokens": 1234, "output_tokens": 56}
}
```

## Python Quick Start

```python
import os, json, urllib.request

TYPESAFEAI_KEY = os.environ['TYPESAFEAI_KEY']
url = 'https://api.typesafe.ai/v1/systemone'

state = {'canonical_substrate': {'doctrines': ['Cells are scars, not parameters.']}}
questions = {
    'q1': {'type': 'noul', 'instructions': 'Is this substrate-canonical: "Cells are scars, not parameters"?'}
}

req = urllib.request.Request(url, data=json.dumps({'model': 'jev-latest', 'state': state, 'questions': questions}).encode(),
                             headers={'Authorization': f'Bearer {TYPESAFEAI_KEY}', 'Content-Type': 'application/json'})
response = json.loads(urllib.request.urlopen(req).read())
print(response['answers']['q1']['noul'])  # e.g. 0.99
```

## Use Cases for Substrate Validation

### 1. Validate a single submission

```python
from jev_quilt.typesafe_client import TypeSafeBackend
backend = TypeSafeBackend()
state = {'submission_text': '...'}
questions = [
    {'name': 'is_canonical', 'type': 'noul', 'instructions': 'Is this canonically aligned?'}
]
decisions, meta = backend.decide_batch(state, questions)
print(f"Answer: {decisions[0].value}, confidence: {decisions[0].confidence}")
```

### 2. Run the JEV Oracle (production validator)

```bash
python3 jev_oracle.py submission.md
```

Or in code:
```python
from jev_oracle import validate
result = validate(submission_text)
print(f"Verdict: {result['verdict']}")
print(f"Voice: {result['voice_score']:.3f}")
print(f"Doctrine: {result['doctrine_score']:.3f}")
print(f"Misquote: {result['misquote_score']:.3f}")
```

### 3. Batch probe multiple questions

```python
questions = [
    {'name': 'voice', 'type': 'noul', 'instructions': 'Is this Fleet Radio voice?'},
    {'name': 'doctrine_scar', 'type': 'noul', 'instructions': 'Are cells scars, not parameters?'},
    {'name': 'verdict', 'choice', 'instructions': 'How canonical is this?',
     'options': {'strong': 'strongly aligned', 'weak': 'weakly aligned', 'none': 'not aligned'}},
]
decisions, meta = backend.decide_batch(state, questions)
```

## Best Practices

### 1. Always pass rich state

JEV accuracy on substrate questions:
- Bare state: ~33%
- Rich state (canonical doctrines): **85.3%**

Always include canonical facts in state when probing substrate questions.

### 2. Use `noul` for yes/no

Returns a probability 0.0-1.0. Treat ≥0.5 as yes, <0.5 as no.

### 3. Use `choice` for ranking

JEV picks the highest-probability option. Returns probabilities for all options.

### 4. Use `score` for rubric

Returns a number 0-4 (or however many criteria). Use 5-level rubrics.

### 5. Handle JEV's hedging

JEV returns 0.40-0.60 when genuinely uncertain. Treat this as ambiguous and re-prompt with more context.

### 6. Don't expect drift

JEV is highly stable: 0 flips across 5 iterations, std ≤ 0.013. If you see different answers for the same input, something else changed.

## Common Gotchas

1. **Don't send the submission as `state` directly** — wrap in a dict with `submission_text` or similar key
2. **Don't put prose in `instructions` longer than ~4000 chars** — JEV may truncate
3. **Don't ask multiple questions in one `instructions` string** — separate into question objects
4. **Watch token usage** — large states (>5000 tokens) increase latency and cost

## Performance

| Batch size | Latency | Tokens (input) |
|---|---|---|
| 1 | ~300ms | ~1500 |
| 14 (oracle) | ~300ms | ~2500 |
| 34 (full battery) | ~700ms | ~3000 |
| 41 (deep probe) | ~600ms | ~3500 |

JEV amortizes batch latency well — sending 20 questions costs ~600ms.

## Examples

### Test if a new piece is canonical

```python
from jev_oracle import validate
result = validate(open('new_piece.md').read())
if result['verdict'].startswith('ACCEPT'):
    print("This piece is canonical-aligned")
elif result['verdict'].startswith('REVIEW'):
    print("Review for subtle doctrine issues")
else:
    print(f"Issue: {result['verdict']}")
```

### Build a custom probe battery

```python
from jev_quilt.typesafe_client import TypeSafeBackend

backend = TypeSafeBackend()
state = {'my_canon': {...}}

# Ask 10 questions about the submission
submission = "..."
questions = [
    {'name': f'q{i}', 'type': 'noul', 'instructions': f'Is "{submission}" {aspect}?'}
    for i, aspect in enumerate(['canonical', 'Fleet Radio', 'doctrinal', ...])
]

decisions, meta = backend.decide_batch(state, questions)
for d in decisions:
    print(f"{d.kind}: {d.value} (conf={d.confidence:.2f})")
```

## Files

- `jev_quilt/typesafe_client.py` — Python client
- `jev_oracle.py` — Production submission validator
- `JEV_ORACLE_SPEC.md` — Oracle spec
- `JEV_LEARNINGS.md` — Findings from 13 sessions
- `tests/test_jev_oracle.py` — 6/6 test cases

## Further Reading

- 12+ session JSON files in `jev_sessions/` document probe results
- `JEV_SESSION_SUMMARY.md` for the executive summary
- Compare JEV vs other models in `session_2_compare.json`
