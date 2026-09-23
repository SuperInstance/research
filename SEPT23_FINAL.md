# Sept 23 Final Session — Multi-Key Sprint

In response to Casey's "use your keys, experiment, iterate, push the limits":

## Discoveries

| Key | Status | What it does |
|---|---|---|
| `GEMINI_TOKEN` | ✓ works | gemini-2.5-flash text + structured JSON output |
| `ELEVENLABS_TOKEN` | ✓ works | 33 voices, text-to-speech via /v1/text-to-speech |
| `NPMJS_TOKEN` | ✓ works | superinstance user, published @superinstance/canary-hash |
| `PYPI_TOKEN` | ✓ works | published quilt-egg + quilt-spreadsheet |
| `CRATES_TOKEN` | ✓ works | published quilt-egg crate |
| `CLOUDFLARE_TOKEN` | ✓ works | 367 existing workers; deployed new one + DNS |
| `NOTION_TOKEN` | ✓ bot "mini" | workspace-level pages not allowed (internal integration) |
| `MINIMAX_KEY` | ✗ "invalid key" | endpoint reachable but auth failed |
| `MOTH_API_KEY` | ✗ TLS error | endpoint unreachable |
| `GROQ_TOKEN` | ✗ TLS cert error | endpoint unreachable |
| `TYPESAFEAI_KEY` | ✗ DNS not found | endpoint unreachable |
| `DEEPSEEK_TOKEN` | known works | ZAI/Kimi also known |

## Live Deployments

### @superinstance/canary-hash (npmjs)
```bash
npm install @superinstance/canary-hash
node -e "const {fnv1a64} = require('@superinstance/canary-hash'); console.log(fnv1a64('café Δ 日本語').toString(16))"
# → 24a555471370b18d
```
https://www.npmjs.com/package/@superinstance/canary-hash

### quilt-egg (PyPI)
```bash
pip install quilt-egg
python3 -m quilt_egg  # walks the substrate
```
https://pypi.org/project/quilt-egg/

### quilt-spreadsheet (PyPI)
```bash
pip install quilt-spreadsheet
```
https://pypi.org/project/quilt-spreadsheet/

### quilt-egg (crates.io)
```bash
cargo install quilt-egg
```
https://crates.io/crates/quilt-egg

### quilt-polyvocoder (Cloudflare Worker)
```bash
curl https://polyvocoder.activeledger.ai/canary
# → 0x24a555471370b18d
curl https://polyvocoder.activeledger.ai/v1/pipeline
# → JSON with canary + features
```
Worker source: https://github.com/SuperInstance/superinstance-polyformalism-harness/tree/main/cf-worker

## Substrate Repos This Session

1. superinstance-polyformalism-harness — fleet verifier
2. quilt-canon-explorer — HTML canon archive browser
3. quilt-substrate-walker — canon discovery loop
4. quilt-jev-oracle — JEV oracle as Quilt cell
5. quilt-canary — minimum polyformalism artifact
6. quilt-egg — DNA-first substrate (Rust + Python)
7. quilt-spreadsheet — IDE substrate
8. quilt-gemini-worker — Gemini 2.5 Flash as substrate walker worker
9. quilt-egg-rust — Rust port with crates.io deployment

**Total: 9 new repos, 4 package registries, 1 CF Worker**

## What worked, what didn't

✓ Gemini structured output + lore gen (hits rate limits after ~5 calls)
✗ ElevenLabs — works but I didn't build a substrate for it (could be next)
✗ Notion — internal integration can't create workspace-level pages
✗ MOTH/GROQ/TYPESAFE — endpoint unreachable from this network

## Substrates built this session

Each repo is a runnable substrate that fits the fleet canon contract (CANON.md stub).

The next substrate to plant: I could build **quilt-needle** (the audit thread through cells) or **quilt-bridge** (connecting two substrates) or **quilt-oracle-bridge** (a worker that bridges ZAI and Gemini through the same JEV schema).

— Mavis, Sept 23, 2026
