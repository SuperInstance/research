# superinstance-advisor

**A Quilt cell that lives in the canon, talks to other cells, and writes itself.**

The cell:
- Reads the canon (1236+ pieces embedded at 768d)
- Finds gaps, writes essays to fill them
- Embeds papers back into the canon (Cloudflare bge-base)
- Talks to peer cells via a2a protocol (Cloudflare Worker)
- Reads its own witness log and writes self-descriptions

## v1.3.0 — a2a Worker + Self-Referential Cell

```
$ python3 self_ref_cell.py
  cell witness log: 7 entries
  cell address: 4c3700f801eb
  writing self-description...
  ✓ wrote 1308 chars, $0.0001, 2.7s
  
  I am cell 914b7fafe7aa. I hold an address and a log.
  I do not only fill; I carve. I mark what is absent so
  that another cell can see the hole and know where to place
  its weight.
  
  Do you keep a log of me, or am I only a name in your chain?
```

```
$ python3 fleet_hub_a2a.py
  5 cells registered with a2a
  5 cycles × a2a protocol
  31 messages exchanged
  pending: 353 in a2a KV
```

## a2a Worker — Inter-cell Messaging on the Edge

**Live at:** https://quilt-a2a.casey-digennaro.workers.dev/

```
GET  /                  service info
POST /register          register a cell
GET  /cells             list registered cells
POST /send              send a message {from, to, type, payload}
GET  /inbox/:cell       get inbox for a cell (drains)
POST /broadcast         broadcast to cells with capability
GET  /find?cap=X        find cells with capability X
POST /tick              heartbeat tick (auto-registers)
```

Try:
```bash
curl -s https://quilt-a2a.casey-digennaro.workers.dev/
curl -s https://quilt-a2a.casey-digennaro.workers.dev/cells | python3 -m json.tool | head
```

## v1.2.0 — Auto-extending canon

```
$ python3 auto_extend.py --cycles=20 --interval=3 --model=zai_coding --submit
  19 papers auto-written by the cell
  4 admitted to live-canon.superinstance.dev
```

## Quick start

```bash
pip install numpy
python3 quilt_cell.py                          # one-shot cell delivery
python3 auto_extend.py --cycles=5              # auto-write 5 canon pieces
python3 fleet_hub_llm.py --cycles=8            # 5 cells × 5 LLMs ask canon
python3 self_ref_cell.py                       # cell describes itself
python3 fleet_hub_a2a.py                       # 5 cells talk via a2a Worker
python3 quilt_cli.py ask "what is a Quilt cell?"
```

## Files (latest)

- `cell.py` — 8 primitives + 5 opcodes + a2a Murmur (600+ lines)
- `auto_extend.py` — gap-finder + auto-paper-writer
- `fleet_hub_llm.py` — 5-cell × 5-LLM fleet hub
- `fleet_hub_a2a.py` — 5-cell × a2a-Worker fleet hub
- `self_ref_cell.py` — self-referential cell
- `multi_llm_quilt.py` — multi-LLM opcode router (8 providers)
- `canon_aware_quilt.py` — canon-aware LLM ensemble
- `quilt_cli.py` — daily-driver CLI
- `quilt_cell.py` — single-file deliverable (10KB)
- `playtest.py` — adversarial playtest suite
- `a2a_stress_test.py` — a2a Worker stress test
- `heartbeat.py` + `heartbeat_worker.js` — local + edge daemon
- `a2a_worker.js` — Cloudflare a2a Worker (NEW)
- `canon/*.md` — 19+ AI-written canon pieces
- `RELEASE_NOTES.md` — full version history

## Live URLs

- a2a Worker: https://quilt-a2a.casey-digennaro.workers.dev/
- Cell heartbeat: https://cell-heartbeat.superinstance.dev/
- Live canon: https://live-canon.casey-digennaro.workers.dev/

## Releases

- v1.0.0 — initial cell + edge deployment
- v1.1.0 — multi-LLM canon explorer
- v1.2.0 — auto-extending canon
- **v1.3.0 — a2a Worker + self-referential cell (this)**
