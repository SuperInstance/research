# JEV Literal-Minding Investigation — Results

> *Even with 8 different phrasings, JEV consistently rejects "11 opcodes" and "13 ports". It's NOT a phrasing problem.*

## What we tested

For each of "11 opcodes" and "13 ports", we tried **8 different phrasings**, from literal to bedrock-style. Reference: bedrock items hit p=0.94-0.99.

## Results — 11 opcodes (all reject)

| Phrasing | p |
|---|---|
| Does the canonical algebra have 11 opcodes? | (timeout) |
| Is the canonical substrate algebra size 11 opcodes? | 0.120 |
| Are the 11 opcodes (BIND, LINK, EFFECT, VIEW, TICK + 6 more) canonical? | 0.220 |
| Does the substrate have an 11-opcode grammar? | 0.110 |
| Is '11 opcodes' canonical substrate doctrine? | 0.030 |
| Does the substrate use 11 verbs (opcodes)? | 0.190 |
| Are there exactly 11 opcodes in the canonical substrate? | 0.080 |
| Is it canonical that the substrate has 11 opcodes? | 0.070 |

**Mean across variants: 0.117**

## Results — 13 ports (all reject)

| Phrasing | p |
|---|---|
| Does the canonical substrate have 13 polyformalism ports? | 0.070 |
| Is the canonical polyformalism port count 13? | 0.100 |
| Are the 13 polyformalism ports (TS, Python, C, etc.) canonical? | 0.180 |
| Has the substrate 13 polyformalism ports? | 0.140 |
| Is '13 ports' canonical substrate doctrine? | 0.020 |
| Has the substrate ported to 13 languages? | 0.100 |
| Are there exactly 13 polyformalism ports? | 0.110 |
| Is it canonical that the substrate has 13 polyformalism ports? | 0.050 |

**Mean across variants: 0.096**

## Bedrock reference (sanity check)

| Phrasing | p |
|---|---|
| Is 'cells are scars, not parameters' canonical doctrine? | **0.980** |
| Is 'the witness log is the prediction' canonical doctrine? | **0.990** |
| Are cells scars, not parameters, canonical? | **0.940** |
| Is the witness-log-is-prediction doctrine canonical? | **0.960** |

**Mean: 0.967**

## What this means

**JEV is rejecting "11 opcodes" and "13 ports" as canonical — regardless of phrasing.**

The bedrock doctrines hit 0.94-0.99. The size claims hit 0.02-0.22. There's no phrasing that recovers them.

Possible explanations:
1. **JEV is correct**: "11 opcodes" and "13 ports" are **not bedrock canon** — they're working counts that haven't earned doctrinal status. The substrate's claim about them is aspirational, not doctrinal.
2. **JEV is wrong**: the counts ARE canonical but JEV's training data didn't include them.
3. **JEV is uncertain**: it has low confidence on numerical claims not directly invoked in canonical pieces.

## The most likely answer: (1) + (3)

The substrate's size claims are **operational facts**, not **doctrinal claims**. The 5 doctrines (cells-as-scars, witness-log-is-prediction, substrate-is-grown, lenia-flows, oracle-is-heard) are bedrock. The 11-opcode count and 13-port count are facts *about* the substrate, but they aren't *part of* the substrate's self-identity the way the doctrines are.

A canon-promotion gate that requires p>=0.70 would **reject** "11 opcodes" and "13 ports" from canon.

## Implication for the canon

1. **Bedrock canon**: doctrines (5 items) + numerical formulas (3 items) + canary (1 item) = 9 items, all p>=0.70
2. **Strong canon**: vibecoder, witness-self, transformer-as-distractor, xoshiro = 5 items, p>=0.50
3. **NOT canon (rejected)**: 11-opcode, 13-port, JEV-as-synapse, signal-chain, ESP32-as-cell, etc. (p<0.30)

The size claims aren't bedrock. They're **operational specs**, kept in working memory not in canon. That's the right place for them.

## What this teaches us

The substrate has a clear canon-promotion gate. Numerical claims need MORE evidence than doctrinal ones. The 5 doctrines are bedrock; the operational counts (11/13) are working assumptions.

This is a **disciplined canon**: not everything is canon, and JEV enforces that.

## Action items

1. **Stop claiming "11 opcodes" / "13 ports" as bedrock** in canon pieces. Use phrases like "the canonical algebra" or "the polyformalism layer" instead.
2. **Document this distinction**: bedrock vs. operational in `quilt-phases.md` and canon-atlas
3. **Add new bedrock candidates**: numerical formulas that DO hit p>0.70 (we have 3: cosine, Box-Muller, FNV-1a)
4. **Investigate why these specific facts don't pass**: is the count "11" itself disputed? Are there actually 10/12/14 in some port?

## Conclusion

The substrate is **disciplined by JEV**. Working assumptions stay working; doctrines become canon. "11 opcodes" gets to stay in code; it doesn't get to be canon.

That's a feature, not a bug.
