#!/bin/bash
# Math layer RSI GAN — 8 topics, 4 providers
# Output: /workspace/repos/ai-writings/cellular-first-design/reports/math_rsi_gan/

REPO=/workspace/repos/ai-writings/bots/rsi-gan
OUT=/workspace/repos/ai-writings/cellular-first-design/reports/math_rsi_gan
mkdir -p "$OUT"

# Math topics — each one a seed for a 250-word prose piece
TOPICS=(
  "What the FNV-1a 64-bit hash 0xbf27a3631cdee337 actually proves: write 250 words on byte-exactness as the substrate's verification property."
  "The cells of Quilt as scars, not parameters: 250 words on why computation is healed tissue, not built structure."
  "Cosine similarity is angle, not distance: write 250 words on what this means for the substrate's semantic search."
  "The witness log is a prediction: 250 words on the JEV × JEPA Rosetta stone where validator and predictor are reflections."
  "Bell states collapse only to 00 or 11: 250 words on measurement as creative destruction."
  "Box-Muller from two uniforms: 250 words on how substrate-rng makes a Gaussian from a coin flip."
  "Polyformalism: the same cell in 13 languages produces the same hash. 250 words on why this is verification, not just porting."
  "The substrate's dance doctrine: cells TICK, JEV scores, parameters breathe. 250 words."
)

PROMPT_ARGS=""
for i in "${!TOPICS[@]}"; do
  TOPIC="${TOPICS[$i]}"
  echo "=== Round $i: $TOPIC ==="
  python3 "$REPO/rsi_gan.py" --prompt "$TOPIC" --rounds 3 --providers zai,groq,deepinfra 2>&1 | tee "$OUT/round_$i.log" | tail -5
  # Move winners
  if [ -d "$REPO/winners" ]; then
    mkdir -p "$OUT/winners_$i"
    cp "$REPO/winners"/* "$OUT/winners_$i/" 2>/dev/null
  fi
done

echo ""
echo "=== ALL ROUNDS COMPLETE ==="
ls -la "$OUT"/
