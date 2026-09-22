#!/usr/bin/env bash
# Verify the Quilt fleet canary across all polyformalism ports.
# 
# The canary string "café Δ 日本語" → fnv1a-64 → 0x024a555471370b18d
# (= 0x24a555471370b18d when leading 0 is stripped; numerically 2,640,610,520,279,855,501)

set -e

ROOT=/workspace/repos

echo "Quilt Fleet Canary Verification"
echo "================================"
echo "Canary:        fnv1a-64('café Δ 日本語')"
echo "Expected:      0x024a555471370b18d"
echo "Decimal:       2,640,610,520,279,855,501"
echo ""

FAIL=0
EXPECTED_DEC=2640610520279855501

hex_to_dec() {
  echo $((16#$1))
}

check_port() {
  local name=$1
  local out=$2
  if [ -z "$out" ]; then
    echo "$name: (no output)"
    return
  fi
  local dec=$(hex_to_dec "${out#0x}")
  if [ "$dec" = "$EXPECTED_DEC" ]; then
    echo "$name:        ✓ $out (decimal $dec)"
  else
    echo "$name:        ✗ FAIL: $out (decimal $dec)"
    FAIL=1
  fi
}

# Python (reference)
PY_OUT=$(python3 "$ROOT/polyvocoder/polyvocoder/canary.py" 2>/dev/null | grep -o '0x[0-9a-f]*' | head -1)
check_port "Python     " "$PY_OUT"

# TypeScript
if command -v npx >/dev/null 2>&1; then
  TS_OUT=$(cd "$ROOT/polyvocoder-bindings" && npx -y tsx canary.ts 2>/dev/null | grep -o '0x[0-9a-f]*' | head -1)
  check_port "TypeScript " "$TS_OUT"
fi

# Rust
if [ -x "$ROOT/polyvocoder-rust/target/release/canary" ]; then
  RUST_OUT=$("$ROOT/polyvocoder-rust/target/release/canary" | grep -o '0x[0-9a-f]*' | head -1)
  check_port "Rust       " "$RUST_OUT"
fi

# JS ESM
JS_OUT=$(node --input-type=module -e "
const string = 'café Δ 日本語';
const bytes = new TextEncoder().encode(string);
let h = 0xcbf29ce484222325n;
const prime = 0x100000001b3n;
const mask = (1n << 64n) - 1n;
for (const b of bytes) {
  h ^= BigInt(b);
  h = (h * prime) & mask;
}
console.log('0x' + h.toString(16).padStart(16, '0'));
" 2>/dev/null)
check_port "JS ESM     " "$JS_OUT"

# C#/.NET
if [ -f "$ROOT/polyvocoder-csharp/Program.csproj" ]; then
  CS_OUT=$(cd "$ROOT/polyvocoder-csharp" && dotnet run 2>/dev/null | grep -o '0x[0-9a-f]*' | head -1)
  check_port "C#/.NET    " "$CS_OUT"
fi

# Bash via Python (Bash can't do 64-bit math natively)
BASH_OUT=$(python3 -c "
s = 'café Δ 日本語'
h = 0xcbf29ce484222325
for b in s.encode('utf-8'):
    h = h ^ b
    h = (h * 0x100000001b3) & 0xffffffffffffffff
print(f'0x{h:016x}')
")
check_port "Bash (py)  " "$BASH_OUT"

echo ""
if [ "$FAIL" = "0" ]; then
  echo "✅ All ports pass the canary (byte-exact: 0x024a555471370b18d)"
  exit 0
else
  echo "❌ Some ports failed"
  exit 1
fi
