const CANARY = "café Δ 日本語";

export function fnv1a_64(s: string): bigint {
  const bytes = new TextEncoder().encode(s);
  let h = 0xcbf29ce484222325n;
  const prime = 0x100000001b3n;
  const mask = (1n << 64n) - 1n;
  for (const b of bytes) {
    h ^= BigInt(b);
    h = (h * prime) & mask;
  }
  return h;
}

export function canary(): string {
  return "0x" + fnv1a_64(CANARY).toString(16).padStart(16, "0");
}

if (typeof require !== "undefined" && require.main === module) {
  console.log(canary());
}
