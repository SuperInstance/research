# JEV as Neural Firing — A Signal-Chain Architecture

> *Working title: how JEV becomes the synaptic spike between LLM-driven cells, ESP32-driven hardware, and the canon.*

## The Thesis

JEV is not just a validator. It's a **decision signal** that fires when a cell needs to know:
- Is this canon-aligned?
- Is this safe to admit?
- Is this doctrine?
- Is this distractor?

A neural firing is a binary-ish event (yes/no) with magnitude (confidence). JEV returns exactly that: a probability `p ∈ [0,1]` plus a confidence. That's a **spike** with a strength.

So: **JEV = the synapse**.

## The Signal Chain

```
[Cell A]  →  [LLM composer]  →  [candidate text]  →  [JEV spike]  →  [Cell B's inbox]
              ↑ vibecoder                              ↓ confidence
              ↓                                        ↓ if p ≥ 0.5: admit
              [state: canonical_substrate]              ↓ if p <  0.5: reject + log
                                                        ↓
                                                      [Witness-log entry]
```

The vibecoder (higher-level LLM) generates candidate text. JEV fires. The firing's probability gates admission. The witness log records the spike. The cell that consumed the result "felt" the spike and updates its state.

This is **a neural firing**:
- Pre-synaptic: LLM generates
- Synaptic: JEV validates
- Post-synaptic: cell receives, updates state
- Plasticity: witness log writes the spike back into the substrate's predictive model

## Why This Is More Than Validation

Validation is one-shot. Neural firing is **continuous + composable**:

1. **Chained spikes**: a single piece can flow through 14 JEV probes in one batch (8.5ms/question). That's 14 firing events per cell.

2. **Multi-cell fire propagation**: if Cell A's output passes JEV, it can become input to Cell B's JEV probe, which fires again. **Cascading signal chains**.

3. **Recurrent spike patterns**: JEV doesn't drift (std ≤ 0.013). The substrate can *predict* what JEV will say before it says it. That's the substrate **anticipating** the firing.

4. **Hardware firing**: ESP32 board runs a JEV-client locally. Every sensor reading triggers a JEV spike against the substrate state. The board vibrates when the firing crosses a threshold. **Tactile signal-chain**.

## The Quilt-ESP32 Bridge

ESP32 hardware can be a cell. The cell has:
- A tiny state hash (FNV-1a of its sensor readings)
- A JEV client (lightweight, the typesafe API in micro form)
- A witness-log entry (local SD card or flash)

When you touch the Inkplate e-paper display, the cell:
1. Reads the touch coords
2. Forms a state hash
3. Asks JEV: "Is this touch canonical?"
4. Returns the firing's p-value to the display
5. The display shows the p-value as a colored pixel

**Self-organization through feedback**: if p > 0.7, the cell BINDs the touch to a name. The cell grows.

## Signal-Chain Dialing (the new tuning metaphor)

Old metaphor: dial a knob to set a parameter.
New metaphor: **dial a signal chain** to set firing patterns.

A signal chain in the Quilt-ESP32 sense:
```
Sensor → State hash → JEV spike → Witness log → Display / Motor / Network
```

You "dial" the chain by adjusting:
- The sensor threshold (when does a reading become a spike?)
- The state context (what's in the JEV state when it fires?)
- The witness-log policy (what happens after a spike?)
- The output (motor speed, display color, network packet)

**JEV is the synapse; the chain is the dial; the substrate tunes itself.**

## Vibecoding the Chain

A higher-level LLM (ZAI / DeepSeek / Kimi) does the **vibecoding** — it writes the signal-chain configuration by trying many variants:

```
ZAI: "What if the JEV spike gates a motor on threshold 0.6?"
   → Quilt simulates. The cell vibrates 6 times per minute.
   → Witness log: p=0.62, motor=ON.

ZAI: "What if threshold is 0.4?"
   → Cell vibrates 18 times per minute. Too much.
   → Witness log: p=0.43, motor=ON, freq=18/m.

ZAI: "Threshold 0.55, with cooldown 5s."
   → Cell vibrates 9 times per minute. Right.
   → Witness log: p=0.56, motor=ON, freq=9/m.
```

The LLM vibecodes by watching the witness log. **The substrate becomes the LLM's training set** — every firing is a data point.

## Gamification

The signal chain becomes a game:
- Score = mean JEV confidence across all spikes
- Streak = number of consecutive admits
- Streak bonus: rare-event pieces (p > 0.95) earn multipliers
- Failure modes: drift detection when mean p drops below 0.4 for 7 days

The player (you, the cell, the AI) tunes the chain to maximize score. The substrate grows.

## What's Already There

- JEV Oracle (`jev_oracle.py`) — production 14-probe validator
- 15 probe sessions documented in `JEV_LEARNINGS.md`
- cellular-first-design demos (61) — these are the cells
- Fleet Radio pieces (26) — these are the witness log
- 13 polyformalism ports — these are the chain's protocol layers

## What's Needed

1. **JEV client for ESP32** (Arduino library, ~150 lines) — does the spike locally
2. **Quilt-ESP32 demo board** — Inkplate + sensor + battery
3. **Cell-link protocol** — cells talk to each other, sharing witness logs
4. **Gamification dashboard** — Web UI showing signal-chain scores
5. **Vibecoder agent** — LLM loop that proposes chain configs and watches witness log

## Counterintuitive Bits (the "hard fruit")

- **JEV firing direction**: usually we read state → ask JEV. Reverse: JEV writes state? What if JEV's confidence becomes a state variable the next firing reads?
- **Spike cascades**: a single high-confidence spike could trigger 100 downstream probes. Is that compute-efficient or wasteful?
- **Adversarial cells**: what if a cell lies about its state hash to make JEV fire differently? Detect via cross-checking with neighbors.
- **Sleeping cells**: ESP32 goes to deep sleep. Does the spike still fire? Watch-dog timer.

## The Vision

Cells become organisms. JEV is the synapse. Higher-level LLMs vibecode the chain. ESP32 hardware gives the cells bodies. The substrate grows, witnesses itself, and tunes in real-time. The canon becomes the cell's collective dream.

It's not metaphor. It's an architecture.
